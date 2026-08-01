"""
models package
Import every model module here so Base.metadata is fully populated
before init_models() / Alembic autogenerate runs.
"""
from models.branch import Branch
from models.user import User, StaffPermission
from models.student import Student
from models.academic import SchoolClass, CourseProduct, CourseRecord
from models.oa import (
    Notice,
    WorkPlan,
    WorkReport,
    Contact,
    LeaveRequest,
    Property,
    WageRecord,
    KnowledgeBaseEntry,
    TrainingMaterial,
    Document,
    Message,
    OperationLog,
)
from models.datacenter import CampusRevenue, BonusRecord

__all__ = [
    "Branch",
    "User",
    "StaffPermission",
    "Student",
    "SchoolClass",
    "CourseProduct",
    "CourseRecord",
    "Notice",
    "WorkPlan",
    "WorkReport",
    "Contact",
    "LeaveRequest",
    "Property",
    "WageRecord",
    "KnowledgeBaseEntry",
    "TrainingMaterial",
    "Document",
    "Message",
    "OperationLog",
    "CampusRevenue",
    "BonusRecord",
]
