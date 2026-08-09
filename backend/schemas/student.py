"""
schemas/student.py
Student schemas — field names mirror MemberList.vue mock data exactly
(camelCase aliases) so the Vue frontend can consume API responses with
zero remapping in Batch 7.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.common import ORMBase, TimestampOut, BusinessStatus, Gender


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class StudentBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(min_length=1, max_length=60)
    gender: Gender = Gender.MALE
    age: int = Field(ge=1, le=99)
    status: BusinessStatus = BusinessStatus.INTENT
    class_info: str | None = None
    phone: str | None = None
    remark: str | None = None
    counselor: str | None = None


class StudentCreate(StudentBase):
    branch_id: str
    class_id: str | None = None


class StudentUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str | None = None
    gender: Gender | None = None
    age: int | None = None
    status: BusinessStatus | None = None
    class_info: str | None = None
    class_id: str | None = None
    phone: str | None = None
    remark: str | None = None
    counselor: str | None = None


class StudentOut(StudentBase, TimestampOut):
    id: str
    branch_id: str
    total_paid: float = 0
    stored: float = 0
    regular_hours: float = Field(0, alias="regular")
    gift_hours: float = Field(0, alias="gift")
    other_hours: float = Field(0, alias="other")
    consumed: float = 0
    absence: int = 0
    on_time_rate: str | None = None
    last_consume: str | None = None
    consume_freq: str | None = None
    last_contact: str | None = None
    next_contact: str | None = None
    review_views: int = 0
    view_rate: str | None = None


class StudentListSummary(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    total: int
    active: int
    on_time: int
    revenue: float


class StudentPageOut(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    total: int
    page: int
    page_size: int
    items: list[StudentOut]
    summary: StudentListSummary


class StudentClassOptionOut(BaseModel):
    id: str
    name: str
    branch_id: str


class DeletedStudentOut(StudentBase, ORMBase):
    id: str
    branch_id: str
    original_student_id: str
    total_paid: float = 0
    stored: float = 0
    regular_hours: float = Field(0, alias="regular")
    gift_hours: float = Field(0, alias="gift")
    other_hours: float = Field(0, alias="other")
    consumed: float = 0
    absence: int = 0
    on_time_rate: str | None = None
    last_consume: str | None = None
    consume_freq: str | None = None
    last_contact: str | None = None
    next_contact: str | None = None
    review_views: int = 0
    view_rate: str | None = None
    student_created_at: datetime | None = None
    student_updated_at: datetime | None = None
    deleted_at: datetime
