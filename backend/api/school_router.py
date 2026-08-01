"""
api/school_router.py
Academic affairs: SchoolClass, CourseProduct, CourseRecord CRUD, plus a
dedicated PATCH action for submitting a course review (CourseReview.vue's
'提交点评' button) and an attendance summary endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_permission
from core.security import Permission
from db.session import get_db
from models.academic import CourseProduct, CourseRecord, SchoolClass
from schemas.academic import (
    CourseProductCreate, CourseProductOut, CourseProductUpdate,
    CourseRecordCreate, CourseRecordOut, CourseReviewSubmit,
    SchoolClassCreate, SchoolClassOut, SchoolClassUpdate,
)
from schemas.common import PageOut
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/school", tags=["school"])

class_crud = CRUDBase(SchoolClass)
product_crud = CRUDBase(CourseProduct)
record_crud = CRUDBase(CourseRecord)


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
