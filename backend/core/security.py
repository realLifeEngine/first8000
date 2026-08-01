"""
core/security.py
Password hashing, JWT issue/verify, and the 4-role RBAC hierarchy with
29 granular permission keys that school_admin can grant/revoke per staff
member (StaffPermission overrides, enforced at the dependency layer in
Batch 4).
"""
from __future__ import annotations

import enum
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

# --------------------------------------------------------------------------
# Password hashing
# --------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --------------------------------------------------------------------------
# Role hierarchy
# --------------------------------------------------------------------------
class Role(str, enum.Enum):
    TEACHER = "teacher"
    MANAGER = "manager"
    SCHOOL_ADMIN = "school_admin"
    SUPERUSER = "superuser"


ROLE_RANK: dict[str, int] = {role: idx for idx, role in enumerate(settings.ROLE_HIERARCHY)}


def role_at_least(user_role: str, minimum_role: str) -> bool:
    """True if user_role is >= minimum_role in the hierarchy."""
    return ROLE_RANK.get(user_role, -1) >= ROLE_RANK.get(minimum_role, 999)


# --------------------------------------------------------------------------
# 29 granular permission keys
# school_admin can grant/revoke any of these to staff via StaffPermission
# override rows, independent of their base role.
# --------------------------------------------------------------------------
class Permission(str, enum.Enum):
    # Front desk / students
    STUDENT_VIEW = "student:view"
    STUDENT_CREATE = "student:create"
    STUDENT_EDIT = "student:edit"
    STUDENT_DELETE = "student:delete"
    STUDENT_EXPORT = "student:export"
    # Academic affairs
    CLASS_MANAGE = "class:manage"
    COURSE_RECORD_MANAGE = "course_record:manage"
    COURSE_REVIEW_SUBMIT = "course_review:submit"
    COURSE_PRODUCT_MANAGE = "course_product:manage"
    ATTENDANCE_MANAGE = "attendance:manage"
    # OA
    NOTICE_PUBLISH = "notice:publish"
    WORK_PLAN_MANAGE = "work_plan:manage"
    WORK_REPORT_MANAGE = "work_report:manage"
    CONTACT_VIEW = "contact:view"
    LEAVE_REQUEST_APPROVE = "leave_request:approve"
    LEAVE_REQUEST_SUBMIT = "leave_request:submit"
    PROPERTY_MANAGE = "property:manage"
    WAGE_VIEW_ALL = "wage:view_all"
    WAGE_MANAGE = "wage:manage"
    KNOWLEDGE_BASE_MANAGE = "knowledge_base:manage"
    TRAINING_MANAGE = "training:manage"
    DOCUMENT_MANAGE = "document:manage"
    MESSAGE_SEND = "message:send"
    AUDIT_LOG_VIEW = "audit_log:view"
    # Data center
    REVENUE_VIEW = "revenue:view"
    BONUS_MANAGE = "bonus:manage"
    CAMPUS_DATA_VIEW = "campus_data:view"
    # Branch / org admin
    BRANCH_MANAGE = "branch:manage"
    STAFF_PERMISSION_GRANT = "staff_permission:grant"


assert len(Permission) == 29, f"Expected 29 permissions, got {len(Permission)}"

# Default permission sets baked in per role; school_admin can layer
# StaffPermission overrides on top of these at runtime (Batch 4).
DEFAULT_ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.TEACHER: {
        Permission.STUDENT_VIEW,
        Permission.COURSE_RECORD_MANAGE,
        Permission.COURSE_REVIEW_SUBMIT,
        Permission.CONTACT_VIEW,
        Permission.LEAVE_REQUEST_SUBMIT,
        Permission.KNOWLEDGE_BASE_MANAGE,
        Permission.MESSAGE_SEND,
    },
    Role.MANAGER: {
        Permission.STUDENT_VIEW,
        Permission.STUDENT_CREATE,
        Permission.STUDENT_EDIT,
        Permission.CLASS_MANAGE,
        Permission.COURSE_RECORD_MANAGE,
        Permission.COURSE_REVIEW_SUBMIT,
        Permission.COURSE_PRODUCT_MANAGE,
        Permission.ATTENDANCE_MANAGE,
        Permission.WORK_PLAN_MANAGE,
        Permission.WORK_REPORT_MANAGE,
        Permission.CONTACT_VIEW,
        Permission.LEAVE_REQUEST_APPROVE,
        Permission.LEAVE_REQUEST_SUBMIT,
        Permission.TRAINING_MANAGE,
        Permission.MESSAGE_SEND,
        Permission.REVENUE_VIEW,
    },
    Role.SCHOOL_ADMIN: {p for p in Permission if p not in {Permission.BRANCH_MANAGE}},
    Role.SUPERUSER: set(Permission),
}


# --------------------------------------------------------------------------
# JWT access / refresh tokens
# --------------------------------------------------------------------------
class TokenType(str, enum.Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, role: str, branch_id: str | None = None) -> str:
    return _create_token(
        subject=user_id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={"role": role, "branch_id": branch_id},
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        subject=user_id,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Raises jose.JWTError on invalid/expired token; caller handles HTTP 401."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise exc
