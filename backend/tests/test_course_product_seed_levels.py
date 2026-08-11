from scripts.seed import build_course_product_seed_rows


def test_build_course_product_seed_rows_creates_one_product_per_level() -> None:
    rows = build_course_product_seed_rows(branch_id="branch-1")

    assert len(rows) == 5
    assert [row["name"] for row in rows] == [
        "编程启蒙",
        "编程基础",
        "编程进阶",
        "编程高阶",
        "算法编程",
    ]
    assert all(row["related_properties"]["课程分类"][0]["分类"] == row["name"] for row in rows)
