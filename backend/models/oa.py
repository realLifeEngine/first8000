"""
models/oa.py
Office/OA module — 12 models backing the OA routes in the frontend router:
notices, work plans, work reports, contacts, leave requests (go-out
registration), property, wages, knowledge base, training, documents,
messages, and operation (audit) logs.
"""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from models.base import UUIDPKMixin, TimestampMixin, BranchScopedMixin


class Notice(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "notices"
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(60), nullable=True)
    publisher_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="已发布")
    create_time: Mapped[str | None] = mapped_column(String(30), nullable=True)


class WorkPlan(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "work_plans"
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    owner: Mapped[str | None] = mapped_column(String(60), nullable=True)
    owner_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    priority: Mapped[str] = mapped_column(String(10), default="中")  # 高/中/低
    deadline: Mapped[str | None] = mapped_column(String(30), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    read: Mapped[str] = mapped_column(String(10), default="未读")


class WorkReport(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "work_reports"
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str | None] = mapped_column(String(60), nullable=True)
    author_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    period: Mapped[str | None] = mapped_column(String(30), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="待审")


class Contact(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "contacts"
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    dept: Mapped[str | None] = mapped_column(String(60), nullable=True)
    role: Mapped[str | None] = mapped_column(String(30), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)


class LeaveRequest(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    """Go-out / leave registration (请假条 / 外出登记)."""
    __tablename__ = "leave_requests"
    applicant: Mapped[str | None] = mapped_column(String(60), nullable=True)
    applicant_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[str | None] = mapped_column(String(30), nullable=True)
    end_time: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="审批中")  # 审批中/已批准/已驳回
    approver_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)


class Property(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "properties"
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    custodian: Mapped[str | None] = mapped_column(String(60), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="使用中")


class WageRecord(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "wage_records"
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    dept: Mapped[str | None] = mapped_column(String(60), nullable=True)
    period: Mapped[str | None] = mapped_column(String(20), nullable=True)
    base_salary: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    bonus: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    deduction: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)


class KnowledgeBaseEntry(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "knowledge_base_entries"
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(60), nullable=True)


class TrainingMaterial(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "training_materials"
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    teacher: Mapped[str | None] = mapped_column(String(60), nullable=True)
    permission: Mapped[str | None] = mapped_column(String(30), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    starred: Mapped[bool] = mapped_column(Boolean, default=False)
    update_time: Mapped[str | None] = mapped_column(String(30), nullable=True)


class Document(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "documents"
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    uploader: Mapped[str | None] = mapped_column(String(60), nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Message(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "messages"
    sender_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    receiver_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False)


class OperationLog(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "operation_logs"
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    action: Mapped[str | None] = mapped_column(String(120), nullable=True)
    module: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
