"""
scripts/seed.py
Ports the Vue frontend's mockData.js generation logic into Python so
seeded SQLite data visually matches the existing UI — this makes visual
regression testing trivial during the Batch 7 API cutover.

Run with:  PYTHONPATH=. python3 scripts/seed.py
"""
from __future__ import annotations

import asyncio
import random

from db.session import session_scope, init_models
from core.security import hash_password
import models as m

random.seed(42)


def rnd(a: int, b: int) -> int:
    return random.randint(a, b)


BUSINESS_STATUSES = ["意向", "正常", "停课", "结课", "流失"]
GENDERS = ["男", "女"]

TEACHERS = [
    {"username": "musajiang", "name": "买乌拉·木沙江", "nickname": "木沙江老师", "role_title": "教务主任", "phone": "13800002201", "dept": "教务部"},
    {"username": "rexida", "name": "热西达", "nickname": "热老师", "role_title": "钢琴教师", "phone": "13900005522", "dept": "教学组"},
    {"username": "wangli", "name": "王丽", "nickname": "王老师", "role_title": "英语教师", "phone": "13600009087", "dept": "教学组"},
    {"username": "chenxiaoming", "name": "陈晓明", "nickname": "陈老师", "role_title": "美术教师", "phone": "13700003345", "dept": "教学组"},
    {"username": "linxiaoyu", "name": "林小雨", "nickname": "林老师", "role_title": "舞蹈教师", "phone": "13500007712", "dept": "教学组"},
    {"username": "zhangwei", "name": "张伟", "nickname": "张老师", "role_title": "数学教师", "phone": "13300004456", "dept": "教学组"},
    {"username": "liufang", "name": "刘芳", "nickname": "刘老师", "role_title": "学管老师", "phone": "13200009981", "dept": "学管部"},
    {"username": "zhaomin", "name": "赵敏", "nickname": "赵老师", "role_title": "语文教师", "phone": "13100006623", "dept": "教学组"},
]

CHINESE_NAMES = ["艾力江", "古丽努尔", "阿卜力克木", "娜迪拉", "买买提", "热依拉", "阿依努尔", "艾合买提",
                 "买尔哈巴", "萨拉", "图尔逊", "帕提古丽", "艾克拜尔", "木尼拉", "阿迪力", "夏依旦",
                 "买合木提", "古丽仙", "艾散", "热娜古丽"]

CLASS_INFOS = ["钢琴精品班", "舞蹈基础班", "美术创意班", "英语启蒙班", "数学思维班"]
CONSUME_FREQS = ["每周2次", "每周3次", "每周1次"]
COURSE_NAMES = ["钢琴基础", "舞蹈提升", "美术创意", "英语口语", "数学思维"]
COURSE_PRODUCT_NAMES = ["钢琴基础入门", "舞蹈形体训练", "创意美术启蒙", "英语口语进阶", "数学思维拓展",
                        "声乐发声训练", "书法基础", "围棋启蒙", "编程思维"]
PRODUCT_CATEGORIES = ["音乐类", "舞蹈类", "美术类", "语言类", "思维类"]


async def seed() -> None:
    await init_models()

    async with session_scope() as db:
        # --- Branches ---
        branch_main = m.Branch(name="总校区", code="MAIN", address="乌鲁木齐市天山区", phone="0991-1234567")
        branch_a = m.Branch(name="分校区A", code="BR-A", address="乌鲁木齐市沙依巴克区")
        branch_b = m.Branch(name="分校区B", code="BR-B", address="乌鲁木齐市新市区")
        db.add_all([branch_main, branch_a, branch_b])
        await db.flush()
        branches = [branch_main, branch_a, branch_b]

        # --- Superuser (not in TEACHERS list) ---
        superuser = m.User(
            username="admin", hashed_password=hash_password("admin123"),
            name="系统管理员", nickname="超级管理员", role="superuser",
            branch_id=branch_main.id, dept="总部",
        )
        db.add(superuser)

        # --- Teachers -> Users ---
        role_map = {"教务主任": "manager", "学管老师": "manager"}
        users = []
        for t in TEACHERS:
            user = m.User(
                username=t["username"], hashed_password=hash_password("teacher123"),
                name=t["name"], nickname=t["nickname"], phone=t["phone"], dept=t["dept"],
                role=role_map.get(t["role_title"], "teacher"),
                branch_id=random.choice(branches).id,
            )
            db.add(user)
            users.append(user)
        await db.flush()

        # --- Course Products ---
        course_products = []
        for i, name in enumerate(COURSE_PRODUCT_NAMES):
            cp = m.CourseProduct(
                seq=i + 1, name=name, product=PRODUCT_CATEGORIES[i % 5], difficulty=rnd(1, 5),
                version=f"v{i % 3 + 1}.0",
                info="本课程系统讲解基础知识与技能训练方法，配套教具与教材。",
                goal="培养学员基础技能与兴趣，建立扎实的学习基础。",
                branch_id=branch_main.id,
            )
            db.add(cp)
            course_products.append(cp)
        await db.flush()

        # --- Students ---
        students = []
        for i in range(32):
            status = BUSINESS_STATUSES[i % len(BUSINESS_STATUSES)]
            total_paid = rnd(3000, 28000)
            name = CHINESE_NAMES[i % len(CHINESE_NAMES)] + (str(i) if i > 19 else "")
            student = m.Student(
                name=name, gender=GENDERS[i % 2], age=rnd(5, 15), status=status,
                class_info=CLASS_INFOS[i % 5], total_paid=total_paid, consumed=rnd(10, 80),
                on_time_rate=f"{rnd(70, 100)}%", counselor=users[i % len(users)].nickname,
                phone=f"1{rnd(30, 39)}****{rnd(1000, 9999)}", remark="",
                regular_hours=rnd(5, 40), gift_hours=rnd(0, 8), other_hours=rnd(0, 3),
                stored=rnd(0, 5000), absence=rnd(0, 6),
                last_consume=f"2026-07-{rnd(1, 28):02d}", consume_freq=CONSUME_FREQS[i % 3],
                last_contact=f"2026-07-{rnd(1, 28):02d}", next_contact=f"2026-08-{rnd(1, 10):02d}",
                review_views=rnd(2, 40), view_rate=f"{rnd(50, 100)}%",
                branch_id=random.choice(branches).id,
            )
            db.add(student)
            students.append(student)
        await db.flush()

        # --- School Classes ---
        for i in range(14):
            sc = m.SchoolClass(
                name=f"{COURSE_NAMES[i % 5]}-{i + 1}号班",
                course_product_id=course_products[i % len(course_products)].id,
                teacher_id=users[i % len(users)].id,
                capacity=15, enrolled=rnd(6, 14),
                schedule=["周一/周三/周五 16:00-17:30", "周二/周四 17:30-19:00", "周末 09:00-10:30"][i % 3],
                status=["进行中", "已结束", "待开班"][i % 3],
                branch_id=random.choice(branches).id,
            )
            db.add(sc)

        # --- Course Records ---
        for i in range(26):
            reviewed = i % 3 != 0
            cr = m.CourseRecord(
                date=f"2026-07-{rnd(1, 30):02d}", time=f"{14 + (i % 6)}:00",
                student_id=students[i % len(students)].id,
                teacher_id=users[i % len(users)].id,
                course_product_id=course_products[i % len(course_products)].id,
                topic=["第" + str(i % 12 + 1) + "课", "进阶练习", "复习巩固"][i % 3],
                duration=[45, 60, 90][i % 3],
                status="已评" if reviewed else "待评",
                comment="本次课堂表现积极，理解能力良好，建议加强练习巩固。" if reviewed else None,
                rating=rnd(3, 5) if reviewed else None,
                branch_id=random.choice(branches).id,
            )
            db.add(cr)

        # --- Notices ---
        notice_titles = ["暑期排课安排", "教师培训通知", "系统升级公告", "薪资调整说明"]
        for i in range(10):
            db.add(m.Notice(
                title=f"关于{notice_titles[i % 4]}的通知 {i + 1}",
                content="各位同事，现将近期工作安排通知如下，请各部门认真落实并按时反馈执行情况。",
                publisher=users[i % len(users)].nickname, publisher_id=users[i % len(users)].id,
                status=["正常", "进行中", "已完成"][i % 3],
                create_time=f"2026-07-{rnd(1, 30):02d} {rnd(8, 18):02d}:00",
                branch_id=branch_main.id,
            ))

        # --- Work Plans ---
        plan_titles = ["暑期招生方案", "教师排班优化", "校区环境整改", "家长满意度调研"]
        for i in range(12):
            db.add(m.WorkPlan(
                title=f"{plan_titles[i % 4]} {i + 1}", owner=users[i % len(users)].nickname,
                owner_id=users[i % len(users)].id, priority=["高", "中", "低"][i % 3],
                deadline=f"2026-08-{rnd(1, 20):02d}", progress=rnd(10, 100),
                feedback="进展顺利" if i % 2 == 0 else "待反馈",
                read="已读" if i % 2 == 0 else "未读", branch_id=branch_main.id,
            ))

        # --- Work Reports ---
        report_titles = ["教学质量周报", "招生月度总结", "校区运营专项报告"]
        for i in range(8):
            db.add(m.WorkReport(
                title=f"{report_titles[i % 3]} {i + 1}", author=users[i % len(users)].nickname,
                author_id=users[i % len(users)].id, period=["周报", "月报", "专项报告"][i % 3],
                content="本周/月教学与运营情况总结，各项指标稳步提升，具体数据见附表。",
                status="待审", branch_id=branch_main.id,
            ))

        # --- Contacts (from teachers) ---
        for u, t in zip(users, TEACHERS):
            db.add(m.Contact(
                name=u.name, dept=u.dept, role=t["role_title"], phone=u.phone,
                email=f"{t['username']}@kaku-edu.cn", branch_id=u.branch_id,
            ))

        # --- Leave Requests ---
        reasons = ["学员家访沟通", "参加行业培训", "个人事务请假"]
        for i in range(9):
            approved = i % 3 != 0
            db.add(m.LeaveRequest(
                applicant=users[i % len(users)].nickname, applicant_id=users[i % len(users)].id,
                reason=reasons[i % 3], start_time=f"2026-07-{rnd(1, 30):02d} {9 + i % 5}:00",
                end_time=f"2026-07-{rnd(1, 30):02d} {13 + i % 5}:00",
                status="已批准" if approved else "审批中",
                approver_id=users[0].id if approved else None,
                branch_id=branch_main.id,
            ))

        # --- Properties ---
        prop_names = ["钢琴", "投影仪", "空调", "打印机", "音响设备", "画架", "课桌椅", "电脑"]
        for i in range(10):
            value = rnd(1500, 25000)
            db.add(m.Property(
                name=prop_names[i % 8], category=["教学设备", "办公设备", "乐器"][i % 3],
                quantity=rnd(1, 5), location=["总校区", "分校区A"][i % 2],
                custodian=users[i % len(users)].nickname,
                status="已报废" if i % 5 == 0 else "正常", branch_id=branch_main.id,
            ))

        # --- Wage Records ---
        for i, u in enumerate(users):
            base = 4500 + i * 300
            bonus = 1200 + i * 200
            db.add(m.WageRecord(
                user_id=u.id, name=u.nickname, dept=u.dept, period="2026-07",
                base_salary=base, bonus=bonus, deduction=0, total=base + bonus,
                branch_id=u.branch_id,
            ))

        # --- Knowledge Base ---
        for i in range(6):
            db.add(m.KnowledgeBaseEntry(
                title=f"常见问题解答 {i + 1}", category=["产品手册", "话术库", "流程规范"][i % 3],
                content="知识库详细内容说明，涵盖常见场景与标准应答话术。",
                author=users[i % len(users)].nickname, branch_id=branch_main.id,
            ))

        # --- Training Materials ---
        for i in range(6):
            db.add(m.TrainingMaterial(
                title=f"内部培训素材 {i + 1}", type=["培训资料", "话术模板", "案例分析"][i % 3],
                teacher=users[i % len(users)].nickname,
                permission=["全员可见", "管理层可见"][i % 2],
                detail="培训详细内容，包含课件与案例讲解。", starred=i % 2 == 0,
                update_time=f"2026-07-{10 + i}", branch_id=branch_main.id,
            ))

        # --- Documents ---
        for i in range(8):
            db.add(m.Document(
                name=f"文件柜文档 {i + 1}", category=["合同", "制度", "模板"][i % 3],
                uploader=users[i % len(users)].nickname, file_url=f"/files/doc_{i + 1}.pdf",
                size=f"{rnd(100, 5000)}KB", branch_id=branch_main.id,
            ))

        # --- Messages ---
        for i in range(5):
            db.add(m.Message(
                sender_id=users[i % len(users)].id, receiver_id=users[(i + 1) % len(users)].id,
                content=f"站内信息通知 {i + 1}", read=i % 2 == 0, branch_id=branch_main.id,
            ))

        # --- Operation Logs ---
        actions = ["修改学员信息", "新增消课记录", "删除课程评价", "调整班级"]
        for i in range(15):
            db.add(m.OperationLog(
                user_id=users[i % len(users)].id, action=actions[i % 4],
                module=["学员资料", "消课记录", "课程评价", "班级信息"][i % 4],
                ip=f"10.0.0.{rnd(2, 254)}", detail="字段变更详情说明信息。",
                branch_id=branch_main.id,
            ))

        # --- Campus Revenue ---
        for i, br in enumerate(branches):
            sign_amount = 180000 + i * 42000
            refund_amount = 8000 + i * 1500
            db.add(m.CampusRevenue(
                period="2026-07", revenue=sign_amount - refund_amount,
                new_students=22 + i * 6, renewals=rnd(10, 30), refunds=refund_amount,
                branch_id=br.id,
            ))

        # --- Bonus Records ---
        for i, u in enumerate(users):
            db.add(m.BonusRecord(
                user_id=u.id, name=u.nickname, period="2026-07",
                amount=2000 + i * 500, category=["招生奖", "续费奖", "满勤奖"][i % 3],
                branch_id=u.branch_id,
            ))

    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
