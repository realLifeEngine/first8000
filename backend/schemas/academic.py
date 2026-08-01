"""
schemas/academic.py
SchoolClass, CourseProduct, CourseRecord schemas — field names/enums
mirror ClassManage.vue / CourseProducts.vue / CourseReview.vue.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.common import ORMBase, TimestampOut, CourseRecordStatus


class SchoolClassBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    course_product_id: str | None = None
    teacher_id: str | None = None
    capacity: int = 0
    enrolled: int = 0
    schedule: str | None = None
    status: str = "进行中"


class SchoolClassCreate(SchoolClassBase):
    branch_id: str


class SchoolClassUpdate(BaseModel):
    name: str | None = None
    course_product_id: str | None = None
    teacher_id: str | None = None
    capacity: int | None = None
    enrolled: int | None = None
    schedule: str | None = None
    status: str | None = None


class SchoolClassOut(SchoolClassBase, TimestampOut):
    id: str
    branch_id: str


class CourseProductBase(BaseModel):
    seq: int = 0
    name: str = Field(min_length=1, max_length=120)
    product: str | None = None
    difficulty: int = Field(3, ge=1, le=5)
    version: str | None = None
    info: str | None = None
    goal: str | None = None


class CourseProductCreate(CourseProductBase):
    branch_id: str


class CourseProductUpdate(BaseModel):
    name: str | None = None
    product: str | None = None
    difficulty: int | None = Field(None, ge=1, le=5)
    version: str | None = None
    info: str | None = None
    goal: str | None = None


class CourseProductOut(CourseProductBase, TimestampOut):
    id: str
    branch_id: str


class CourseRecordBase(BaseModel):
    date: str
    time: str | None = None
    student_id: str
    teacher_id: str | None = None
    course_product_id: str | None = None
    topic: str | None = None
    duration: float = 1.0
    status: CourseRecordStatus = CourseRecordStatus.PENDING
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = None


class CourseRecordCreate(CourseRecordBase):
    branch_id: str


class CourseReviewSubmit(BaseModel):
    """PATCH payload for submitting a review — used by CourseReview.vue's '提交点评'."""
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1, max_length=2000)


class CourseRecordOut(CourseRecordBase, TimestampOut):
    id: str
    branch_id: str
