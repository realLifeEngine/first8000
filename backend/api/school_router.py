"""
api/school_router.py
Academic affairs: SchoolClass, CourseProduct, CourseRecord CRUD, plus a
dedicated PATCH action for submitting a course review (CourseReview.vue's
'提交点评' button) and an attendance summary endpoint.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_permission
from core.security import Permission
from db.session import get_db
from models.academic import ClassStudentMembership, CourseProduct, CourseRecord, SchoolClass
from models.student import Student
from models.user import User
from schemas.academic import (
    CourseProductCreate, CourseProductOut, CourseProductUpdate,
    CourseRecordCreate, CourseRecordOut, CourseReviewSubmit,
    SchoolClassCreate, SchoolClassOut, SchoolClassUpdate,
)
from schemas.common import PageOut
from schemas.student import StudentOut
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/school", tags=["school"])

class_crud = CRUDBase(SchoolClass)
product_crud = CRUDBase(CourseProduct)
record_crud = CRUDBase(CourseRecord)


async def _sync_class_enrolled(db: AsyncSession, class_id: str) -> None:
    count_query = select(func.count()).select_from(ClassStudentMembership).where(ClassStudentMembership.class_id == class_id)
    enrolled = (await db.execute(count_query)).scalar_one()
    school_class = await class_crud.get(db, class_id)
    school_class.enrolled = int(enrolled)


async def _sync_student_class_info(db: AsyncSession, student_id: str) -> None:
    student = await db.get(Student, student_id)
    if student is None:
        return
    class_name = (
        await db.execute(
            select(SchoolClass.name)
            .join(ClassStudentMembership, ClassStudentMembership.class_id == SchoolClass.id)
            .where(ClassStudentMembership.student_id == student_id)
            .order_by(desc(ClassStudentMembership.created_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    student.class_info = class_name


# --- Classes ---
@router.get("/classes", response_model=PageOut)
async def list_classes(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CLASS_MANAGE.value))) -> PageOut:
    items, total = await class_crud.list(db, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[SchoolClassOut.model_validate(i) for i in items])


@router.post("/classes", response_model=SchoolClassOut, status_code=201)
async def create_class(payload: SchoolClassCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CLASS_MANAGE.value))) -> SchoolClassOut:
    return SchoolClassOut.model_validate(await class_crud.create(db, payload.model_dump()))


@router.put("/classes/{class_id}", response_model=SchoolClassOut)
async def update_class(class_id: str, payload: SchoolClassUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CLASS_MANAGE.value))) -> SchoolClassOut:
    return SchoolClassOut.model_validate(await class_crud.update(db, class_id, payload.model_dump(exclude_unset=True)))


@router.get("/classes/{class_id}/students", response_model=list[StudentOut])
async def list_class_students(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_MANAGE.value)),
) -> list[StudentOut]:
    school_class = await class_crud.get(db, class_id)
    query = (
        select(Student)
        .join(ClassStudentMembership, ClassStudentMembership.student_id == Student.id)
        .where(ClassStudentMembership.class_id == school_class.id)
        .order_by(desc(Student.created_at))
    )
    items = (await db.execute(query)).scalars().all()
    return [StudentOut.model_validate(item) for item in items]


@router.get("/classes/{class_id}/students/available", response_model=list[StudentOut])
async def list_available_students_for_class(
    class_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_MANAGE.value)),
) -> list[StudentOut]:
    school_class = await class_crud.get(db, class_id)
    subquery = select(ClassStudentMembership.student_id).where(ClassStudentMembership.class_id == school_class.id)
    query = (
        select(Student)
        .where(Student.branch_id == school_class.branch_id)
        .where(Student.id.not_in(subquery))
        .order_by(desc(Student.created_at))
    )
    items = (await db.execute(query)).scalars().all()
    return [StudentOut.model_validate(item) for item in items]


@router.post("/classes/{class_id}/students/{student_id}", status_code=200)
async def assign_student_to_class(
    class_id: str,
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_MANAGE.value)),
) -> dict:
    school_class = await class_crud.get(db, class_id)
    student = await db.get(Student, student_id)
    if student is None:
        return {"ok": False, "detail": "Student not found"}
    if student.branch_id != school_class.branch_id:
        return {"ok": False, "detail": "Student and class must belong to the same branch"}

    existing = (
        await db.execute(select(ClassStudentMembership).where(ClassStudentMembership.student_id == student.id).limit(1))
    ).scalar_one_or_none()
    previous_class_id = None
    if existing is None:
        db.add(
            ClassStudentMembership(
                class_id=school_class.id,
                student_id=student.id,
                branch_id=school_class.branch_id,
            )
        )
    else:
        previous_class_id = existing.class_id
        existing.class_id = school_class.id
        existing.branch_id = school_class.branch_id

    await _sync_student_class_info(db, student.id)
    await _sync_class_enrolled(db, school_class.id)
    if previous_class_id and previous_class_id != school_class.id:
        await _sync_class_enrolled(db, previous_class_id)

    await db.commit()
    return {"ok": True}


@router.delete("/classes/{class_id}/students/{student_id}", status_code=200)
async def remove_student_from_class(
    class_id: str,
    student_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.CLASS_MANAGE.value)),
) -> dict:
    school_class = await class_crud.get(db, class_id)
    membership = (
        await db.execute(
            select(ClassStudentMembership)
            .where(ClassStudentMembership.class_id == school_class.id)
            .where(ClassStudentMembership.student_id == student_id)
            .limit(1)
        )
    ).scalar_one_or_none()
    if membership is None:
        return {"ok": False, "detail": "Membership not found"}

    await db.delete(membership)
    await _sync_student_class_info(db, student_id)
    await _sync_class_enrolled(db, school_class.id)
    await db.commit()
    return {"ok": True}


@router.delete("/classes/{class_id}", status_code=204)
async def delete_class(class_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CLASS_MANAGE.value))) -> None:
    await class_crud.delete(db, class_id)


# --- Course Products ---
@router.get("/course-products", response_model=PageOut)
async def list_course_products(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    items, total = await product_crud.list(db, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[CourseProductOut.model_validate(i) for i in items])


@router.post("/course-products", response_model=CourseProductOut, status_code=201)
async def create_course_product(payload: CourseProductCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.COURSE_PRODUCT_MANAGE.value))) -> CourseProductOut:
    return CourseProductOut.model_validate(await product_crud.create(db, payload.model_dump()))


@router.put("/course-products/{product_id}", response_model=CourseProductOut)
async def update_course_product(product_id: str, payload: CourseProductUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.COURSE_PRODUCT_MANAGE.value))) -> CourseProductOut:
    return CourseProductOut.model_validate(await product_crud.update(db, product_id, payload.model_dump(exclude_unset=True)))


@router.delete("/course-products/{product_id}", status_code=204)
async def delete_course_product(product_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.COURSE_PRODUCT_MANAGE.value))) -> None:
    await product_crud.delete(db, product_id)


# --- Course Records / Review ---
@router.get("/course-records", response_model=PageOut)
async def list_course_records(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.COURSE_RECORD_MANAGE.value)),
) -> PageOut:
    items, total = await record_crud.list(db, page=page, page_size=page_size)
    if status_filter:
        items = [i for i in items if i.status == status_filter]
        total = len(items)
    return PageOut(total=total, page=page, page_size=page_size, items=[CourseRecordOut.model_validate(i) for i in items])


@router.post("/course-records", response_model=CourseRecordOut, status_code=201)
async def create_course_record(payload: CourseRecordCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.COURSE_RECORD_MANAGE.value))) -> CourseRecordOut:
    return CourseRecordOut.model_validate(await record_crud.create(db, payload.model_dump()))


@router.patch("/course-records/{record_id}/review", response_model=CourseRecordOut)
async def submit_review(record_id: str, payload: CourseReviewSubmit, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.COURSE_REVIEW_SUBMIT.value))) -> CourseRecordOut:
    """Backs CourseReview.vue's '提交点评' button — sets rating+comment and flips status to 已评."""
    data = {"rating": payload.rating, "comment": payload.comment, "status": "已评"}
    return CourseRecordOut.model_validate(await record_crud.update(db, record_id, data))


# --- Course Index (tree.json backed file browser) ---

_TREE_FILE = Path(__file__).parent.parent / "assets" / "tree.json"


@lru_cache(maxsize=1)
def _load_course_tree() -> dict:
    """Load the course tree from assets/tree.json once per process."""
    if not _TREE_FILE.exists():
        return {}
    with _TREE_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def _flatten_course_tree(node: dict, parent_parts: list[str] | None = None) -> list[dict]:
    """Flatten the nested tree into a list of directory/file entries for pagination."""
    if not isinstance(node, dict):
        return []

    parent_parts = list(parent_parts or [])
    entries: list[dict] = []

    for name, value in node.items():
        if name in {"_self", "_files"}:
            continue
        if not isinstance(value, dict):
            continue

        child_parts = parent_parts + [name]
        entry = {
            "name": name,
            "path": "/".join(child_parts),
            "url": value.get("_self"),
            "is_dir": True,
            "depth": len(child_parts),
        }
        entries.append(entry)
        entries.extend(_flatten_course_tree(value, child_parts))

        files = value.get("_files") or []
        if isinstance(files, list):
            for file_entry in files:
                if not isinstance(file_entry, dict):
                    continue
                file_name = file_entry.get("name")
                if not file_name:
                    continue
                entries.append({
                    "name": file_name,
                    "path": "/".join(child_parts + [file_name]),
                    "url": file_entry.get("url"),
                    "is_dir": False,
                    "depth": len(child_parts) + 1,
                })

    return entries


@router.get("/course-index/products")
async def list_course_index_products(
    _=Depends(get_current_active_user),
) -> list[dict]:
    """Return the top-level course products defined in the tree.json file."""
    tree = _load_course_tree()
    if not isinstance(tree, dict):
        return []

    products = []
    for name in tree.keys():
        if isinstance(name, str):
            products.append({"id": name, "name": name, "in_index": True})
    return products


@router.get("/course-index")
async def get_course_index(
    product: str = Query(..., description="Top-level directory name"),
    page: int = Query(1, ge=1, description="Page number to return"),
    page_size: int = Query(80, ge=1, le=200, description="Maximum number of entries to return"),
    offset: int | None = Query(None, ge=0, description="Legacy offset parameter"),
    limit: int | None = Query(None, ge=1, le=200, description="Legacy limit parameter"),
    _=Depends(get_current_active_user),
) -> dict:
    """Return a paged slice of file/directory entries under the given top-level course directory."""
    tree = _load_course_tree()
    if not isinstance(tree, dict) or product not in tree:
        raise HTTPException(status_code=404, detail="Product not found in index")

    items = _flatten_course_tree(tree[product])
    if offset is not None:
        page = (offset // (limit or page_size)) + 1
    if limit is not None:
        page_size = limit

    total = len(items)
    start = min((page - 1) * page_size, total)
    end = min(start + page_size, total)
    page_items = items[start:end]
    return {
        "product": product,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": end < total,
        "items": page_items,
    }
