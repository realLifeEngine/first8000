"""
api package
api_router aggregates every domain router into a single include for
main.py's app factory (Batch 6).
"""
from fastapi import APIRouter

from api.auth_router import router as auth_router
from api.branch_router import router as branch_router
from api.staff_router import router as staff_router
from api.student_router import router as student_router
from api.school_router import router as school_router
from api.oa_router import router as oa_router
from api.datacenter_router import router as datacenter_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(branch_router)
api_router.include_router(staff_router)
api_router.include_router(student_router)
api_router.include_router(school_router)
api_router.include_router(oa_router)
api_router.include_router(datacenter_router)
