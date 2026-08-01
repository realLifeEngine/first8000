import { createRouter, createWebHashHistory } from 'vue-router'
const Login = () => import('../views/Login.vue')
const DashboardLayout = () => import('../views/DashboardLayout.vue')
const Overview = () => import('../views/Overview.vue')
const MemberList = () => import('../views/frontdesk/MemberList.vue')
const ClassManage = () => import('../views/school/ClassManage.vue')
const CourseRecords = () => import('../views/school/CourseRecords.vue')
const CourseReview = () => import('../views/school/CourseReview.vue')
const CourseProducts = () => import('../views/school/CourseProducts.vue')
const AttendanceStats = () => import('../views/school/AttendanceStats.vue')
const Notices = () => import('../views/oa/Notices.vue')
const WorkPlans = () => import('../views/oa/WorkPlans.vue')
const WorkReports = () => import('../views/oa/WorkReports.vue')
const Contacts = () => import('../views/oa/Contacts.vue')
const GoOutRegister = () => import('../views/oa/GoOutRegister.vue')
const Property = () => import('../views/oa/Property.vue')
const Wage = () => import('../views/oa/Wage.vue')
const KnowledgeBase = () => import('../views/oa/KnowledgeBase.vue')
const Training = () => import('../views/oa/Training.vue')
const Documents = () => import('../views/oa/Documents.vue')
const Messages = () => import('../views/oa/Messages.vue')
const OperationLogs = () => import('../views/oa/OperationLogs.vue')
const RevenueReport = () => import('../views/datacenter/RevenueReport.vue')
const Ranking = () => import('../views/datacenter/Ranking.vue')
const BonusStats = () => import('../views/datacenter/BonusStats.vue')
const CampusData = () => import('../views/datacenter/CampusData.vue')

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: Login },
  { path: '/app', component: DashboardLayout, children: [
    { path: '', redirect: '/app/overview' },
    { path: 'overview', name: 'overview', component: Overview, meta: { crumb: '总览' } },
    { path: 'frontdesk/members', name: 'fd-members', component: MemberList, meta: { crumb: '前台业务 > 会员管理' } },
    { path: 'school/class', name: 'school-class', component: ClassManage, meta: { crumb: '教务管理 > 班级管理' } },
    { path: 'school/course-records', name: 'school-course-records', component: CourseRecords, meta: { crumb: '教务管理 > 教课记录' } },
    { path: 'school/course-review', name: 'school-course-review', component: CourseReview, meta: { crumb: '教务管理 > 消课管理 > 课堂点评' } },
    { path: 'school/course-products', name: 'school-course-products', component: CourseProducts, meta: { crumb: '教务管理 > 课程管理' } },
    { path: 'school/attendance', name: 'school-attendance', component: AttendanceStats, meta: { crumb: '教务管理 > 出勤统计' } },
    { path: 'oa/notices', name: 'oa-notices', component: Notices, meta: { crumb: '办公OA > 内部公文' } },
    { path: 'oa/plans', name: 'oa-plans', component: WorkPlans, meta: { crumb: '办公OA > 工作计划' } },
    { path: 'oa/reports', name: 'oa-reports', component: WorkReports, meta: { crumb: '办公OA > 工作报告' } },
    { path: 'oa/contacts', name: 'oa-contacts', component: Contacts, meta: { crumb: '办公OA > 通讯录' } },
    { path: 'oa/goout', name: 'oa-goout', component: GoOutRegister, meta: { crumb: '办公OA > 请假条' } },
    { path: 'oa/property', name: 'oa-property', component: Property, meta: { crumb: '办公OA > 资产管理' } },
    { path: 'oa/wage', name: 'oa-wage', component: Wage, meta: { crumb: '办公OA > 工资明细' } },
    { path: 'oa/knowledge', name: 'oa-knowledge', component: KnowledgeBase, meta: { crumb: '办公OA > 知识库' } },
    { path: 'oa/training', name: 'oa-training', component: Training, meta: { crumb: '办公OA > 内部培训' } },
    { path: 'oa/documents', name: 'oa-documents', component: Documents, meta: { crumb: '办公OA > 文件柜' } },
    { path: 'oa/messages', name: 'oa-messages', component: Messages, meta: { crumb: '办公OA > 站内短信' } },
    { path: 'oa/logs', name: 'oa-logs', component: OperationLogs, meta: { crumb: '办公OA > 操作记录' } },
    { path: 'data/revenue', name: 'dc-revenue', component: RevenueReport, meta: { crumb: '数据中心 > 业绩统计' } },
    { path: 'data/ranking', name: 'dc-ranking', component: Ranking, meta: { crumb: '数据中心 > 人员排名' } },
    { path: 'data/bonus', name: 'dc-bonus', component: BonusStats, meta: { crumb: '数据中心 > 奖金汇总' } },
    { path: 'data/campus', name: 'dc-campus', component: CampusData, meta: { crumb: '数据中心 > 校区数据' } },
  ] },
  { path: '/:pathMatch(.*)*', redirect: '/app/overview' }
]
const router = createRouter({ history: createWebHashHistory(), routes })
export default router
