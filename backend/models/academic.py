"""
models/academic.py
Academic module: SchoolClass, CourseProduct, CourseRecord.
Field names mirror ClassManage.vue / CourseProducts.vue / CourseReview.vue
mock data so the frontend swap in Batch 7 is a drop-in.
"""
from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base
from models.base import UUIDPKMixin, TimestampMixin, BranchScopedMixin


class SchoolClass(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "school_classes"

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    course_product_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("course_products.id"), nullable=True)
    teacher_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    enrolled: Mapped[int] = mapped_column(Integer, default=0)
    schedule: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="进行中")

    course_product: Mapped["CourseProduct"] = relationship(back_populates="classes")
    student_memberships: Mapped[list["ClassStudentMembership"]] = relationship(
        back_populates="school_class",
        cascade="all, delete-orphan",
    )


class CourseProduct(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "course_products"

    seq: Mapped[int] = mapped_column(Integer, default=0)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    product: Mapped[str | None] = mapped_column(String(80), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=3)  # 1-5 star rating
    version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    duration_spec: Mapped[str | None] = mapped_column(String(60), nullable=True)  # 时间规格, e.g. "45分钟/次"
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)  # 产品单价
    info: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)

    classes: Mapped[list["SchoolClass"]] = relationship(back_populates="course_product")
    course_records: Mapped[list["CourseRecord"]] = relationship(back_populates="course_product")


class CourseRecord(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    """A single teaching session record, feeds the CourseReview workflow."""
    __tablename__ = "course_records"

    date: Mapped[str] = mapped_column(String(20), nullable=False)
    time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id", ondelete="CASCADE"), index=True)
    teacher_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    course_product_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("course_products.id"), nullable=True)
    topic: Mapped[str | None] = mapped_column(String(120), nullable=True)
    duration: Mapped[float] = mapped_column(Numeric(4, 1), default=1.0)
    status: Mapped[str] = mapped_column(String(10), default="待评")  # 待评/已评
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="course_records")
    course_product: Mapped["CourseProduct"] = relationship(back_populates="course_records")


class ClassStudentMembership(Base, UUIDPKMixin, TimestampMixin, BranchScopedMixin):
    __tablename__ = "class_student_memberships"
    __table_args__ = (
        UniqueConstraint("class_id", "student_id", name="uq_class_student_membership"),
        UniqueConstraint("student_id", name="uq_student_single_class_membership"),
    )

    class_id: Mapped[str] = mapped_column(String(36), ForeignKey("school_classes.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[str] = mapped_column(String(36), ForeignKey("students.id", ondelete="CASCADE"), index=True)

    school_class: Mapped["SchoolClass"] = relationship(back_populates="student_memberships")
    student: Mapped["Student"] = relationship(back_populates="class_memberships")
