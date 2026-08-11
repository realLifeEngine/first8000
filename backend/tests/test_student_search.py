from sqlalchemy import select

from api.student_router import _apply_student_filters
from models.student import Student


def test_apply_student_filters_matches_name_or_phone() -> None:
    query = select(Student)
    filtered = _apply_student_filters(
        query,
        branch_filter=None,
        search="帕提古丽",
        name=None,
        business_status=None,
        class_info=None,
        counselor=None,
    )

    compiled = str(filtered.compile(compile_kwargs={"literal_binds": True}))
    assert "student.name" in compiled
    assert "student.phone" in compiled
    assert "帕提古丽" in compiled
