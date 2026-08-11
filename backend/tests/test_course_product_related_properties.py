from schemas.academic import CourseProductCreate


def test_course_product_related_properties_accepts_price_table_payload() -> None:
    payload = CourseProductCreate(
        name="编程启蒙",
        branch_id="branch-1",
        related_properties={
            "institution": "Willook编程中心",
            "title": "价目表",
            "lesson_description": "1课时=45分钟，1次课=2课时",
            "course_categories": [
                {
                    "分类": "编程启蒙",
                    "单价": "75元/课时",
                    "课程": ["3-4岁小小工程师"],
                    "课时价格": [{"课时": 30, "价格": 2250}],
                }
            ],
        },
    )

    assert payload.related_properties["institution"] == "Willook编程中心"
    assert payload.related_properties["course_categories"][0]["课程"][0] == "3-4岁小小工程师"
