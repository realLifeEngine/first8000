from app.models.branch import Branch
from app.models.user import User, StaffPermission
from app.models.student import Student
from app.models.school import SchoolClass, CourseProduct, CourseRecord
from app.models.oa import (
    Notice, WorkPlan, WorkReport, Contact, GoOutRecord,
    PropertyAsset, WageRecord, KnowledgeItem, TrainingItem,
    Document, Message, OperationLog,
)
from app.models.finance import CampusRevenue, BonusRecord

__all__ = [
    "Branch", "User", "StaffPermission", "Student",
    "SchoolClass", "CourseProduct", "CourseRecord",
    "Notice", "WorkPlan", "WorkReport", "Contact", "GoOutRecord",
    "PropertyAsset", "WageRecord", "KnowledgeItem", "TrainingItem",
    "Document", "Message", "OperationLog",
    "CampusRevenue", "BonusRecord",
]
