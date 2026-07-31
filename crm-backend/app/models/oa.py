"""Office Administration (OA) module models."""
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Notice(Base):
    __tablename__ = "notices"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    category: Mapped[str] = mapped_column(String(32), default="行政通知")
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, default="")
    publisher: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(16), default="正常")
    starred: Mapped[bool] = mapped_column(Boolean, default=False)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    create_time: Mapped[str] = mapped_column(String(32), default="")


class WorkPlan(Base):
    __tablename__ = "work_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    owner: Mapped[str] = mapped_column(String(64), default="")
    initiator: Mapped[str] = mapped_column(String(64), default="")
    participants: Mapped[str] = mapped_column(String(32), default="1人")
    priority: Mapped[str] = mapped_column(String(8), default="中")
    progress: Mapped[str] = mapped_column(String(8), default="0")
    deadline: Mapped[str] = mapped_column(String(32), default="")
    read: Mapped[str] = mapped_column(String(8), default="未读")
    feedback: Mapped[str] = mapped_column(Text, default="待反馈")
    create_time: Mapped[str] = mapped_column(String(32), default="")


class WorkReport(Base):
    __tablename__ = "work_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    category: Mapped[str] = mapped_column(String(16), default="周报")
    title: Mapped[str] = mapped_column(String(200))
    dept: Mapped[str] = mapped_column(String(64), default="")
    submitter: Mapped[str] = mapped_column(String(64), default="")
    time: Mapped[str] = mapped_column(String(32), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    read: Mapped[str] = mapped_column(String(8), default="未读")


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    nickname: Mapped[str] = mapped_column(String(64), default="")
    role: Mapped[str] = mapped_column(String(64), default="")
    dept: Mapped[str] = mapped_column(String(64), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    bio: Mapped[str] = mapped_column(Text, default="")


class GoOutRecord(Base):
    __tablename__ = "goout_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    apply_date: Mapped[str] = mapped_column(String(32), default="")
    applicant: Mapped[str] = mapped_column(String(64), default="")
    type: Mapped[str] = mapped_column(String(32), default="请假")
    reason: Mapped[str] = mapped_column(Text, default="")
    out_time: Mapped[str] = mapped_column(String(16), default="")
    back_time: Mapped[str] = mapped_column(String(16), default="")
    absence_days: Mapped[float] = mapped_column(Float, default=0.5)
    audit: Mapped[str] = mapped_column(String(16), default="审批中", index=True)
    audit_time: Mapped[str] = mapped_column(String(32), default="-")
    auditor: Mapped[str] = mapped_column(String(64), default="-")
    dept: Mapped[str] = mapped_column(String(64), default="")
    submit_time: Mapped[str] = mapped_column(String(32), default="")
    detail: Mapped[str] = mapped_column(Text, default="")


class PropertyAsset(Base):
    __tablename__ = "property_assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(32), default="教学设备")
    record_date: Mapped[str] = mapped_column(String(32), default="")
    value: Mapped[str] = mapped_column(String(32), default="0")
    current_value: Mapped[str] = mapped_column(String(32), default="0")
    depreciation_rate: Mapped[str] = mapped_column(String(16), default="10%")
    keeper: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(16), default="正常")
    scrapped: Mapped[str] = mapped_column(String(8), default="否")
    dept: Mapped[str] = mapped_column(String(64), default="")
    entry_time: Mapped[str] = mapped_column(String(32), default="")
    desc: Mapped[str] = mapped_column(Text, default="")


class WageRecord(Base):
    __tablename__ = "wage_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    dept: Mapped[str] = mapped_column(String(64), default="")
    base: Mapped[str] = mapped_column(String(32), default="0")
    bonus: Mapped[str] = mapped_column(String(32), default="0")
    amount: Mapped[str] = mapped_column(String(32), default="0")
    status: Mapped[str] = mapped_column(String(16), default="待发放", index=True)


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    type: Mapped[str] = mapped_column(String(32), default="产品手册")
    qa: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, default="")
    update_time: Mapped[str] = mapped_column(String(32), default="")


class TrainingItem(Base):
    __tablename__ = "training_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    sort: Mapped[int] = mapped_column(Integer, default=1)
    type: Mapped[str] = mapped_column(String(32), default="培训资料")
    starred: Mapped[bool] = mapped_column(Boolean, default=False)
    title: Mapped[str] = mapped_column(String(200))
    permission: Mapped[str] = mapped_column(String(32), default="全员可见")
    detail: Mapped[str] = mapped_column(Text, default="")
    teacher: Mapped[str] = mapped_column(String(64), default="")
    update_time: Mapped[str] = mapped_column(String(32), default="")


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    category: Mapped[str] = mapped_column(String(32), default="合同")
    starred: Mapped[bool] = mapped_column(Boolean, default=False)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    title: Mapped[str] = mapped_column(String(200))
    edit_time: Mapped[str] = mapped_column(String(32), default="")
    publisher: Mapped[str] = mapped_column(String(64), default="")
    create_time: Mapped[str] = mapped_column(String(32), default="")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    sender: Mapped[str] = mapped_column(String(64), default="")
    time: Mapped[str] = mapped_column(String(32), default="")
    read: Mapped[bool] = mapped_column(Boolean, default=False)


class OperationLog(Base):
    __tablename__ = "operation_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    time: Mapped[str] = mapped_column(String(32), default="")
    student: Mapped[str] = mapped_column(String(64), default="")
    action: Mapped[str] = mapped_column(String(120), default="")
    data_type: Mapped[str] = mapped_column(String(64), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    reason: Mapped[str] = mapped_column(String(120), default="")
    auditor: Mapped[str] = mapped_column(String(64), default="")
    campus: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
