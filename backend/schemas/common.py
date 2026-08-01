"""
schemas/common.py
Shared Pydantic base classes and enums used across schema modules.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """Base for *Out schemas that read from SQLAlchemy ORM objects."""
    model_config = ConfigDict(from_attributes=True)


class TimestampOut(ORMBase):
    created_at: datetime
    updated_at: datetime


class BusinessStatus(str, Enum):
    INTENT = "意向"
    NORMAL = "正常"
    SUSPENDED = "停课"
    COMPLETED = "结课"
    LOST = "流失"


class Gender(str, Enum):
    MALE = "男"
    FEMALE = "女"


class CourseRecordStatus(str, Enum):
    PENDING = "待评"
    REVIEWED = "已评"


class ReadStatus(str, Enum):
    READ = "已读"
    UNREAD = "未读"


class ApprovalStatus(str, Enum):
    PENDING = "审批中"
    APPROVED = "已批准"
    REJECTED = "已驳回"


class Priority(str, Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class PayoutStatus(str, Enum):
    PENDING = "待发放"
    PAID = "已发放"


class Role(str, Enum):
    TEACHER = "teacher"
    MANAGER = "manager"
    SCHOOL_ADMIN = "school_admin"
    SUPERUSER = "superuser"


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 10


class PageOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list
