"""
api/oa_router.py
Office/OA module CRUD routes for all 12 entities: notices, work plans,
work reports, contacts, leave requests, property, wages, knowledge base,
training, documents, messages, operation logs (read-only).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, require_permission
from core.security import Permission, ROLE_RANK, role_at_least
from db.session import get_db
from models.oa import (
    Contact, Document, KnowledgeBaseEntry, LeaveRequest, Message, Notice,
    OperationLog, Property, TrainingMaterial, WageRecord, WorkPlan, WorkReport,
)
from models.user import User
from schemas.common import PageOut
from schemas.oa import (
    ContactCreate, ContactOut, ContactUpdate,
    DocumentCreate, DocumentOut,
    KnowledgeBaseEntryCreate, KnowledgeBaseEntryOut, KnowledgeBaseEntryUpdate,
    LeaveRequestApprove, LeaveRequestCreate, LeaveRequestOut,
    MessageCreate, MessageOut,
    NoticeCreate, NoticeOut, NoticeUpdate,
    OperationLogOut,
    OperationLogViewOut,
    PropertyCreate, PropertyOut, PropertyUpdate,
    TrainingMaterialCreate, TrainingMaterialOut, TrainingMaterialUpdate,
    WageRecordCreate, WageRecordOut,
    WorkPlanCreate, WorkPlanOut, WorkPlanUpdate,
    WorkReportCreate, WorkReportOut, WorkReportUpdate,
)
from services.crud import CRUDBase

router = APIRouter(prefix="/api/v1/oa", tags=["oa"])

notice_crud = CRUDBase(Notice)
plan_crud = CRUDBase(WorkPlan)
report_crud = CRUDBase(WorkReport)
contact_crud = CRUDBase(Contact)
leave_crud = CRUDBase(LeaveRequest)
property_crud = CRUDBase(Property)
wage_crud = CRUDBase(WageRecord)
kb_crud = CRUDBase(KnowledgeBaseEntry)
training_crud = CRUDBase(TrainingMaterial)
document_crud = CRUDBase(Document)
message_crud = CRUDBase(Message)
log_crud = CRUDBase(OperationLog)


async def _paged(crud: CRUDBase, out_schema, page: int, page_size: int, db: AsyncSession) -> PageOut:
    items, total = await crud.list(db, page=page, page_size=page_size)
    return PageOut(total=total, page=page, page_size=page_size, items=[out_schema.model_validate(i) for i in items])


def _apply_operation_log_visibility(query, viewer: User):
    if viewer.role == "superuser":
        return query

    # Non-superusers never see superuser actions.
    query = query.where(or_(User.role.is_(None), User.role != "superuser"))

    viewer_rank = ROLE_RANK.get(viewer.role, -1)
    visible_roles = [role for role, rank in ROLE_RANK.items() if rank <= viewer_rank and role != "superuser"]
    query = query.where(or_(User.role.in_(visible_roles), User.role.is_(None), OperationLog.user_id == viewer.id))

    # Teachers/managers are still branch-scoped.
    if not role_at_least(viewer.role, "school_admin"):
        query = query.where(OperationLog.branch_id == viewer.branch_id)

    return query


# --- Notices ---
@router.get("/notices", response_model=PageOut)
async def list_notices(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(notice_crud, NoticeOut, page, page_size, db)

@router.post("/notices", response_model=NoticeOut, status_code=201)
async def create_notice(payload: NoticeCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.NOTICE_PUBLISH.value))) -> NoticeOut:
    return NoticeOut.model_validate(await notice_crud.create(db, payload.model_dump()))

@router.put("/notices/{item_id}", response_model=NoticeOut)
async def update_notice(item_id: str, payload: NoticeUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.NOTICE_PUBLISH.value))) -> NoticeOut:
    return NoticeOut.model_validate(await notice_crud.update(db, item_id, payload.model_dump(exclude_unset=True)))

@router.delete("/notices/{item_id}", status_code=204)
async def delete_notice(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.NOTICE_PUBLISH.value))) -> None:
    await notice_crud.delete(db, item_id)


# --- Work Plans ---
@router.get("/work-plans", response_model=PageOut)
async def list_work_plans(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(plan_crud, WorkPlanOut, page, page_size, db)

@router.post("/work-plans", response_model=WorkPlanOut, status_code=201)
async def create_work_plan(payload: WorkPlanCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WORK_PLAN_MANAGE.value))) -> WorkPlanOut:
    return WorkPlanOut.model_validate(await plan_crud.create(db, payload.model_dump()))

@router.put("/work-plans/{item_id}", response_model=WorkPlanOut)
async def update_work_plan(item_id: str, payload: WorkPlanUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WORK_PLAN_MANAGE.value))) -> WorkPlanOut:
    return WorkPlanOut.model_validate(await plan_crud.update(db, item_id, payload.model_dump(exclude_unset=True)))

@router.delete("/work-plans/{item_id}", status_code=204)
async def delete_work_plan(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WORK_PLAN_MANAGE.value))) -> None:
    await plan_crud.delete(db, item_id)


# --- Work Reports ---
@router.get("/work-reports", response_model=PageOut)
async def list_work_reports(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(report_crud, WorkReportOut, page, page_size, db)

@router.post("/work-reports", response_model=WorkReportOut, status_code=201)
async def create_work_report(payload: WorkReportCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WORK_REPORT_MANAGE.value))) -> WorkReportOut:
    return WorkReportOut.model_validate(await report_crud.create(db, payload.model_dump()))

@router.put("/work-reports/{item_id}", response_model=WorkReportOut)
async def update_work_report(item_id: str, payload: WorkReportUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WORK_REPORT_MANAGE.value))) -> WorkReportOut:
    return WorkReportOut.model_validate(await report_crud.update(db, item_id, payload.model_dump(exclude_unset=True)))

@router.delete("/work-reports/{item_id}", status_code=204)
async def delete_work_report(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WORK_REPORT_MANAGE.value))) -> None:
    await report_crud.delete(db, item_id)


# --- Contacts ---
@router.get("/contacts", response_model=PageOut)
async def list_contacts(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CONTACT_VIEW.value))) -> PageOut:
    return await _paged(contact_crud, ContactOut, page, page_size, db)

@router.post("/contacts", response_model=ContactOut, status_code=201)
async def create_contact(payload: ContactCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CONTACT_VIEW.value))) -> ContactOut:
    return ContactOut.model_validate(await contact_crud.create(db, payload.model_dump()))

@router.put("/contacts/{item_id}", response_model=ContactOut)
async def update_contact(item_id: str, payload: ContactUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CONTACT_VIEW.value))) -> ContactOut:
    return ContactOut.model_validate(await contact_crud.update(db, item_id, payload.model_dump(exclude_unset=True)))

@router.delete("/contacts/{item_id}", status_code=204)
async def delete_contact(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.CONTACT_VIEW.value))) -> None:
    await contact_crud.delete(db, item_id)


# --- Leave Requests ---
@router.get("/leave-requests", response_model=PageOut)
async def list_leave_requests(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(leave_crud, LeaveRequestOut, page, page_size, db)

@router.post("/leave-requests", response_model=LeaveRequestOut, status_code=201)
async def create_leave_request(payload: LeaveRequestCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.LEAVE_REQUEST_SUBMIT.value))) -> LeaveRequestOut:
    return LeaveRequestOut.model_validate(await leave_crud.create(db, payload.model_dump()))

@router.patch("/leave-requests/{item_id}/approve", response_model=LeaveRequestOut)
async def approve_leave_request(item_id: str, payload: LeaveRequestApprove, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.LEAVE_REQUEST_APPROVE.value))) -> LeaveRequestOut:
    data = {"status": payload.status.value, "approver_id": payload.approver_id}
    return LeaveRequestOut.model_validate(await leave_crud.update(db, item_id, data))

@router.delete("/leave-requests/{item_id}", status_code=204)
async def delete_leave_request(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.LEAVE_REQUEST_SUBMIT.value))) -> None:
    await leave_crud.delete(db, item_id)


# --- Properties ---
@router.get("/properties", response_model=PageOut)
async def list_properties(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(property_crud, PropertyOut, page, page_size, db)

@router.post("/properties", response_model=PropertyOut, status_code=201)
async def create_property(payload: PropertyCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.PROPERTY_MANAGE.value))) -> PropertyOut:
    return PropertyOut.model_validate(await property_crud.create(db, payload.model_dump()))

@router.put("/properties/{item_id}", response_model=PropertyOut)
async def update_property(item_id: str, payload: PropertyUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.PROPERTY_MANAGE.value))) -> PropertyOut:
    return PropertyOut.model_validate(await property_crud.update(db, item_id, payload.model_dump(exclude_unset=True)))

@router.delete("/properties/{item_id}", status_code=204)
async def delete_property(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.PROPERTY_MANAGE.value))) -> None:
    await property_crud.delete(db, item_id)


# --- Wages ---
@router.get("/wages", response_model=PageOut)
async def list_wages(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WAGE_VIEW_ALL.value))) -> PageOut:
    return await _paged(wage_crud, WageRecordOut, page, page_size, db)

@router.post("/wages", response_model=WageRecordOut, status_code=201)
async def create_wage(payload: WageRecordCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WAGE_MANAGE.value))) -> WageRecordOut:
    return WageRecordOut.model_validate(await wage_crud.create(db, payload.model_dump()))

@router.delete("/wages/{item_id}", status_code=204)
async def delete_wage(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.WAGE_MANAGE.value))) -> None:
    await wage_crud.delete(db, item_id)


# --- Knowledge Base ---
@router.get("/knowledge-base", response_model=PageOut)
async def list_knowledge_base(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(kb_crud, KnowledgeBaseEntryOut, page, page_size, db)

@router.post("/knowledge-base", response_model=KnowledgeBaseEntryOut, status_code=201)
async def create_knowledge_base(payload: KnowledgeBaseEntryCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.KNOWLEDGE_BASE_MANAGE.value))) -> KnowledgeBaseEntryOut:
    return KnowledgeBaseEntryOut.model_validate(await kb_crud.create(db, payload.model_dump()))

@router.put("/knowledge-base/{item_id}", response_model=KnowledgeBaseEntryOut)
async def update_knowledge_base(item_id: str, payload: KnowledgeBaseEntryUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.KNOWLEDGE_BASE_MANAGE.value))) -> KnowledgeBaseEntryOut:
    return KnowledgeBaseEntryOut.model_validate(await kb_crud.update(db, item_id, payload.model_dump(exclude_unset=True)))

@router.delete("/knowledge-base/{item_id}", status_code=204)
async def delete_knowledge_base(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.KNOWLEDGE_BASE_MANAGE.value))) -> None:
    await kb_crud.delete(db, item_id)


# --- Training ---
@router.get("/training", response_model=PageOut)
async def list_training(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(training_crud, TrainingMaterialOut, page, page_size, db)

@router.post("/training", response_model=TrainingMaterialOut, status_code=201)
async def create_training(payload: TrainingMaterialCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.TRAINING_MANAGE.value))) -> TrainingMaterialOut:
    return TrainingMaterialOut.model_validate(await training_crud.create(db, payload.model_dump()))

@router.put("/training/{item_id}", response_model=TrainingMaterialOut)
async def update_training(item_id: str, payload: TrainingMaterialUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.TRAINING_MANAGE.value))) -> TrainingMaterialOut:
    return TrainingMaterialOut.model_validate(await training_crud.update(db, item_id, payload.model_dump(exclude_unset=True)))

@router.delete("/training/{item_id}", status_code=204)
async def delete_training(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.TRAINING_MANAGE.value))) -> None:
    await training_crud.delete(db, item_id)


# --- Documents ---
@router.get("/documents", response_model=PageOut)
async def list_documents(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(document_crud, DocumentOut, page, page_size, db)

@router.post("/documents", response_model=DocumentOut, status_code=201)
async def create_document(payload: DocumentCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.DOCUMENT_MANAGE.value))) -> DocumentOut:
    return DocumentOut.model_validate(await document_crud.create(db, payload.model_dump()))

@router.delete("/documents/{item_id}", status_code=204)
async def delete_document(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.DOCUMENT_MANAGE.value))) -> None:
    await document_crud.delete(db, item_id)


# --- Messages ---
@router.get("/messages", response_model=PageOut)
async def list_messages(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> PageOut:
    return await _paged(message_crud, MessageOut, page, page_size, db)

@router.post("/messages", response_model=MessageOut, status_code=201)
async def create_message(payload: MessageCreate, db: AsyncSession = Depends(get_db), _=Depends(require_permission(Permission.MESSAGE_SEND.value))) -> MessageOut:
    return MessageOut.model_validate(await message_crud.create(db, payload.model_dump()))

@router.delete("/messages/{item_id}", status_code=204)
async def delete_message(item_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)) -> None:
    await message_crud.delete(db, item_id)


# --- Operation Logs (read-only) ---
@router.get("/operation-logs", response_model=PageOut)
async def list_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    viewer: User = Depends(require_permission(Permission.AUDIT_LOG_VIEW.value)),
) -> PageOut:
    count_query = _apply_operation_log_visibility(
        select(func.count(OperationLog.id)).select_from(OperationLog).outerjoin(User, User.id == OperationLog.user_id),
        viewer,
    )
    total = (await db.execute(count_query)).scalar_one()

    items_query = _apply_operation_log_visibility(
        select(OperationLog, User.role, User.nickname, User.name)
        .outerjoin(User, User.id == OperationLog.user_id)
        .order_by(desc(OperationLog.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size),
        viewer,
    )
    rows = (await db.execute(items_query)).all()

    items = [
        OperationLogViewOut.model_validate(
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "module": log.module,
                "ip": log.ip,
                "detail": log.detail,
                "branch_id": log.branch_id,
                "created_at": log.created_at,
                "updated_at": log.updated_at,
                "actor_name": nickname or name,
                "actor_role": role,
            }
        )
        for log, role, nickname, name in rows
    ]

    return PageOut(total=total, page=page, page_size=page_size, items=items)
