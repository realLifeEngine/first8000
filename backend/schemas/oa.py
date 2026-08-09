"""
schemas/oa.py
Schemas for the 12 OA models. Each entity gets Create/Update/Out for
consistent CRUD routes in Batch 5.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.common import TimestampOut, ReadStatus, Priority, ApprovalStatus, PayoutStatus


class NoticeBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str | None = None
    publisher: str | None = None
    publisher_id: str | None = None
    status: str = "已发布"
    create_time: str | None = None


class NoticeCreate(NoticeBase):
    branch_id: str


class NoticeUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None


class NoticeOut(NoticeBase, TimestampOut):
    id: str
    branch_id: str


class WorkPlanBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    owner: str | None = None
    owner_id: str | None = None
    priority: Priority = Priority.MEDIUM
    deadline: str | None = None
    progress: int = Field(0, ge=0, le=100)
    feedback: str | None = None
    read: ReadStatus = ReadStatus.UNREAD


class WorkPlanCreate(WorkPlanBase):
    branch_id: str


class WorkPlanUpdate(BaseModel):
    title: str | None = None
    priority: Priority | None = None
    deadline: str | None = None
    progress: int | None = Field(None, ge=0, le=100)
    feedback: str | None = None
    read: ReadStatus | None = None


class WorkPlanOut(WorkPlanBase, TimestampOut):
    id: str
    branch_id: str


class WorkReportBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str | None = None
    author_id: str | None = None
    period: str | None = None
    content: str | None = None
    status: str = "待审"


class WorkReportCreate(WorkReportBase):
    branch_id: str


class WorkReportUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None


class WorkReportOut(WorkReportBase, TimestampOut):
    id: str
    branch_id: str


class ContactBase(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    dept: str | None = None
    role: str | None = None
    phone: str | None = None
    email: str | None = None


class ContactCreate(ContactBase):
    branch_id: str


class ContactUpdate(BaseModel):
    dept: str | None = None
    role: str | None = None
    phone: str | None = None
    email: str | None = None


class ContactOut(ContactBase, TimestampOut):
    id: str
    branch_id: str


class LeaveRequestBase(BaseModel):
    applicant: str | None = None
    applicant_id: str | None = None
    reason: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver_id: str | None = None


class LeaveRequestCreate(LeaveRequestBase):
    branch_id: str


class LeaveRequestApprove(BaseModel):
    """PATCH payload for approving/rejecting a leave request."""
    status: ApprovalStatus
    approver_id: str


class LeaveRequestOut(LeaveRequestBase, TimestampOut):
    id: str
    branch_id: str


class PropertyBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str | None = None
    quantity: int = 1
    location: str | None = None
    custodian: str | None = None
    status: str = "使用中"


class PropertyCreate(PropertyBase):
    branch_id: str


class PropertyUpdate(BaseModel):
    quantity: int | None = None
    location: str | None = None
    custodian: str | None = None
    status: str | None = None


class PropertyOut(PropertyBase, TimestampOut):
    id: str
    branch_id: str


class WageRecordBase(BaseModel):
    user_id: str | None = None
    name: str | None = None
    dept: str | None = None
    period: str | None = None
    base_salary: float = 0
    bonus: float = 0
    deduction: float = 0
    total: float = 0


class WageRecordCreate(WageRecordBase):
    branch_id: str


class WageRecordOut(WageRecordBase, TimestampOut):
    id: str
    branch_id: str


class KnowledgeBaseEntryBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str | None = None
    content: str | None = None
    author: str | None = None


class KnowledgeBaseEntryCreate(KnowledgeBaseEntryBase):
    branch_id: str


class KnowledgeBaseEntryUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    content: str | None = None


class KnowledgeBaseEntryOut(KnowledgeBaseEntryBase, TimestampOut):
    id: str
    branch_id: str


class TrainingMaterialBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: str | None = None
    teacher: str | None = None
    permission: str | None = None
    detail: str | None = None
    starred: bool = False
    update_time: str | None = None


class TrainingMaterialCreate(TrainingMaterialBase):
    branch_id: str


class TrainingMaterialUpdate(BaseModel):
    title: str | None = None
    detail: str | None = None
    starred: bool | None = None
    permission: str | None = None


class TrainingMaterialOut(TrainingMaterialBase, TimestampOut):
    id: str
    branch_id: str


class DocumentBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str | None = None
    uploader: str | None = None
    file_url: str | None = None
    size: str | None = None


class DocumentCreate(DocumentBase):
    branch_id: str


class DocumentOut(DocumentBase, TimestampOut):
    id: str
    branch_id: str


class MessageBase(BaseModel):
    sender_id: str | None = None
    receiver_id: str | None = None
    content: str | None = None
    read: bool = False


class MessageCreate(MessageBase):
    branch_id: str


class MessageOut(MessageBase, TimestampOut):
    id: str
    branch_id: str


class OperationLogBase(BaseModel):
    user_id: str | None = None
    action: str | None = None
    module: str | None = None
    ip: str | None = None
    detail: str | None = None


class OperationLogOut(OperationLogBase, TimestampOut):
    id: str
    branch_id: str


class OperationLogViewOut(OperationLogOut):
    actor_name: str | None = None
    actor_role: str | None = None
