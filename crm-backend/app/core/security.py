"""
Security primitives: password hashing, JWT issuance/verification,
and role/permission constants used across the RBAC system.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# Role hierarchy (higher number = more privilege)
# ---------------------------------------------------------------------------
ROLE_TEACHER = "teacher"
ROLE_MANAGER = "manager"
ROLE_SCHOOL_ADMIN = "school_admin"
ROLE_SUPERUSER = "superuser"

ROLE_RANK = {
    ROLE_TEACHER: 1,
    ROLE_MANAGER: 2,
    ROLE_SCHOOL_ADMIN: 3,
    ROLE_SUPERUSER: 4,
}

# Granular permission keys. school_admin can grant/revoke any of these
# (except superuser-only ones) to staff within their own branch.
PERMISSIONS = {
    "branch.manage": "管理校区信息",
    "staff.manage": "管理员工账号",
    "staff.grant_permissions": "分配员工权限",
    "students.view": "查看学员",
    "students.edit": "编辑学员信息",
    "students.delete": "删除学员",
    "classes.manage": "管理班级",
    "courses.manage": "管理课程",
    "course_records.manage": "管理教课记录",
    "course_reviews.manage": "课堂点评",
    "attendance.view": "查看出勤统计",
    "oa.notices.manage": "管理内部公文",
    "oa.plans.manage": "管理工作计划",
    "oa.reports.manage": "管理工作报告",
    "oa.contacts.view": "查看通讯录",
    "oa.goout.manage": "管理请假外出",
    "oa.goout.approve": "审批请假外出",
    "oa.property.manage": "管理资产",
    "oa.wage.view": "查看工资明细",
    "oa.wage.manage": "管理工资明细",
    "oa.knowledge.manage": "管理知识库",
    "oa.training.manage": "管理内部培训",
    "oa.documents.manage": "管理文件柜",
    "oa.messages.view": "查看站内短信",
    "oa.logs.view": "查看操作记录",
    "data.revenue.view": "查看业绩统计",
    "data.ranking.view": "查看人员排名",
    "data.bonus.view": "查看奖金汇总",
    "data.bonus.manage": "管理奖金发放",
    "data.campus.view": "查看校区数据",
}

# Default permission sets granted at account creation time, per role.
# school_admin (or superuser) can subsequently customize per-staff overrides.
DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    ROLE_TEACHER: [
        "students.view",
        "classes.manage",
        "course_records.manage",
        "course_reviews.manage",
        "attendance.view",
        "oa.contacts.view",
        "oa.goout.manage",
        "oa.knowledge.manage",
        "oa.messages.view",
    ],
    ROLE_MANAGER: [
        "students.view", "students.edit",
        "classes.manage", "courses.manage",
        "course_records.manage", "course_reviews.manage",
        "attendance.view",
        "oa.notices.manage", "oa.plans.manage", "oa.reports.manage",
        "oa.contacts.view", "oa.goout.manage", "oa.goout.approve",
        "oa.property.manage", "oa.knowledge.manage", "oa.training.manage",
        "oa.documents.manage", "oa.messages.view",
        "data.ranking.view", "data.campus.view",
    ],
    ROLE_SCHOOL_ADMIN: list(PERMISSIONS.keys()),
    ROLE_SUPERUSER: list(PERMISSIONS.keys()),
}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None


def role_has_min_rank(role: str, min_role: str) -> bool:
    return ROLE_RANK.get(role, 0) >= ROLE_RANK.get(min_role, 99)
