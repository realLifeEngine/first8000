let AUTO_ID = 90000
export function nextId() { return ++AUTO_ID }
function rnd(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a }

export const businessStatuses = ['意向', '正常', '停课', '结课', '流失']
export const genders = ['男', '女']

export const teachers = [
  { id: 4393, name: '买乌拉·木沙江', nickname: '木沙江老师', role: '教务主任', phone: '138****2201', dept: '教务部' },
  { id: 2667, name: '热西达', nickname: '热老师', role: '钢琴教师', phone: '139****5522', dept: '教学组' },
  { id: 3312, name: '王丽', nickname: '王老师', role: '英语教师', phone: '136****9087', dept: '教学组' },
  { id: 5521, name: '陈晓明', nickname: '陈老师', role: '美术教师', phone: '137****3345', dept: '教学组' },
  { id: 6688, name: '林小雨', nickname: '林老师', role: '舞蹈教师', phone: '135****7712', dept: '教学组' },
  { id: 7745, name: '张伟', nickname: '张老师', role: '数学教师', phone: '133****4456', dept: '教学组' },
  { id: 8890, name: '刘芳', nickname: '刘老师', role: '学管老师', phone: '132****9981', dept: '学管部' },
  { id: 9012, name: '赵敏', nickname: '赵老师', role: '语文教师', phone: '131****6623', dept: '教学组' },
]

const chineseNames = ['艾力江','古丽努尔','阿卜力克木','娜迪拉','买买提','热依拉','阿依努尔','艾合买提','买尔哈巴','萨拉','图尔逊','帕提古丽','艾克拜尔','木尼拉','阿迪力','夏依旦','买合木提','古丽仙','艾散','热娜古丽']
export const students = Array.from({ length: 32 }, (_, i) => {
  const status = businessStatuses[i % businessStatuses.length]
  const totalPaid = rnd(3000, 28000)
  return {
    id: 10000 + i, name: chineseNames[i % chineseNames.length] + (i > 19 ? i : ''),
    gender: genders[i % 2], age: rnd(5, 15), status,
    classInfo: ['钢琴精品班', '舞蹈基础班', '美术创意班', '英语启蒙班', '数学思维班'][i % 5],
    totalPaid: totalPaid.toString(), consumed: rnd(10, 80), onTimeRate: rnd(70, 100) + '%',
    counselor: teachers[i % teachers.length].nickname, phone: '1' + rnd(30, 39) + '****' + rnd(1000, 9999),
    remark: '', regular: rnd(5, 40), gift: rnd(0, 8), other: rnd(0, 3), stored: rnd(0, 5000).toString(),
    absence: rnd(0, 6), lastConsume: `2026-07-${rnd(1, 28)}`, consumeFreq: ['每周2次', '每周3次', '每周1次'][i % 3],
    lastContact: `2026-07-${rnd(1, 28)}`, nextContact: `2026-08-${rnd(1, 10)}`,
    reviewViews: rnd(2, 40), viewRate: rnd(50, 100) + '%',
  }
})

export const classes = Array.from({ length: 14 }, (_, i) => ({
  id: 20000 + i, type: ['常规班', '精品班', '集训班', '短期班'][i % 4],
  date: ['周一/周三/周五', '周二/周四', '周末班'][i % 3],
  time: ['16:00-17:30', '17:30-19:00', '09:00-10:30'][i % 3], duration: '90分钟',
  course: ['钢琴基础', '舞蹈提升', '美术创意', '英语口语', '数学思维'][i % 5],
  remark: `${i + 1}号班`, weekTopic: ['节奏训练', '音阶练习', '色彩搭配', '日常对话', '几何图形'][i % 5],
  capacity: `${rnd(6, 14)}/15`, campus: ['总校区', '分校区A', '分校区B'][i % 3],
  weekStatus: ['进行中', '已结束', '待开班'][i % 3], studentInfo: `${rnd(6,14)}人`,
}))

export const courseRecords = Array.from({ length: 26 }, (_, i) => ({
  id: 30000 + i, date: `2026-07-${rnd(1, 30)}`, time: `${14 + (i % 6)}:00`,
  teacher: teachers[i % teachers.length].nickname, student: students[i % students.length].name,
  course: ['钢琴基础', '舞蹈提升', '美术创意', '英语口语', '数学思维'][i % 5],
  topic: ['第' + (i % 12 + 1) + '课', '进阶练习', '复习巩固'][i % 3],
  duration: [45, 60, 90][i % 3], status: i % 3 === 0 ? '待评' : '已评',
  comment: i % 3 !== 0 ? '本次课堂表现积极，理解能力良好，建议加强练习巩固。' : '', rating: i % 3 !== 0 ? rnd(3, 5) : 0,
}))

export const courseProducts = Array.from({ length: 9 }, (_, i) => ({
  id: 40000 + i, seq: i + 1, name: ['钢琴基础入门', '舞蹈形体训练', '创意美术启蒙', '英语口语进阶', '数学思维拓展', '声乐发声训练', '书法基础', '围棋启蒙', '编程思维'][i],
  product: ['音乐类', '舞蹈类', '美术类', '语言类', '思维类'][i % 5], difficulty: rnd(1, 5),
  version: 'v' + (i % 3 + 1) + '.0',
  info: '本课程系统讲解基础知识与技能训练方法，配套教具与教材。',
  goal: '培养学员基础技能与兴趣，建立扎实的学习基础。',
}))

export const notices = Array.from({ length: 10 }, (_, i) => ({
  id: 50000 + i, category: ['行政通知', '教务通知', '人事通知', '系统公告'][i % 4],
  starred: i % 3 === 0, pinned: i % 4 === 0, title: `关于${['暑期排课安排','教师培训通知','系统升级公告','薪资调整说明'][i % 4]}的通知 ${i+1}`,
  publisher: teachers[i % teachers.length].nickname, createTime: `2026-07-${rnd(1, 30)} ${rnd(8,18)}:00`,
  editTime: `2026-07-${rnd(1, 30)}`, status: ['正常', '进行中', '已完成'][i % 3],
  content: '各位同事，现将近期工作安排通知如下，请各部门认真落实并按时反馈执行情况，如有疑问请及时联系行政部。',
}))

export const workPlans = Array.from({ length: 12 }, (_, i) => ({
  id: 60000 + i, read: i % 2 === 0 ? '已读' : '未读', deadline: `2026-08-${rnd(1, 20)}`,
  type: ['日常', '周计划', '专项'][i % 3], priority: ['高', '中', '低'][i % 3],
  title: `${['暑期招生方案','教师排班优化','校区环境整改','家长满意度调研'][i % 4]} ${i+1}`,
  owner: teachers[i % teachers.length].nickname, progress: rnd(10, 100).toString(),
  feedback: i % 2 === 0 ? '进展顺利' : '待反馈', completeTime: '-', participants: rnd(1,5) + '人',
  initiator: teachers[(i+1) % teachers.length].nickname, createTime: `2026-07-${rnd(1,28)}`,
}))

export const workReports = Array.from({ length: 8 }, (_, i) => ({
  id: 70000 + i, read: i % 2 === 0 ? '已读' : '未读', category: ['周报', '月报', '专项报告'][i % 3],
  title: `${['教学质量周报','招生月度总结','校区运营专项报告'][i % 3]} ${i+1}`,
  dept: ['教务部', '市场部', '行政部'][i % 3], submitter: teachers[i % teachers.length].nickname,
  time: `2026-07-${rnd(1, 30)}`, content: '本周/月教学与运营情况总结，各项指标稳步提升，具体数据见附表。',
}))

export const goOutRecords = Array.from({ length: 9 }, (_, i) => ({
  id: 80000 + i, applyDate: `2026-07-${rnd(1, 30)}`, applicant: teachers[i % teachers.length].nickname,
  type: ['家访', '外出培训', '请假'][i % 3], reason: ['学员家访沟通', '参加行业培训', '个人事务请假'][i % 3],
  outTime: `${9 + i % 5}:00`, backTime: `${13 + i % 5}:00`, absenceDays: (i % 3 === 2 ? 1 : 0.5),
  audit: i % 3 === 0 ? '审批中' : '已批准', auditTime: i % 3 !== 0 ? `2026-07-${rnd(1,30)}` : '-',
  auditor: i % 3 !== 0 ? '木沙江老师' : '-', dept: '教务部', submitTime: `2026-07-${rnd(1,30)} 09:00`,
  detail: '外出/请假详细说明',
}))

export const properties = Array.from({ length: 10 }, (_, i) => {
  const value = rnd(1500, 25000)
  return {
    id: 90100 + i, recordDate: `2026-0${rnd(1,7)}-${rnd(1,28)}`, type: ['教学设备', '办公设备', '乐器'][i % 3],
    name: ['钢琴', '投影仪', '空调', '打印机', '音响设备', '画架', '课桌椅', '电脑'][i % 8],
    value: value.toString(), depreciationRate: '10%', currentValue: Math.round(value * 0.85).toString(),
    status: i % 5 === 0 ? '已报废' : '正常', keeper: teachers[i % teachers.length].nickname,
    dept: ['教务部', '行政部'][i % 2], scrapped: i % 5 === 0 ? '是' : '否', desc: '资产设备说明',
    entryTime: `2026-07-${rnd(1,28)} 10:00`,
  }
})

export const contacts = teachers.map((t) => ({
  id: t.id, name: t.name, nickname: t.nickname, role: t.role, phone: t.phone, dept: t.dept,
  bio: `${t.role}，负责${t.dept}相关工作，教学经验丰富。`,
}))

export const wageRecords = teachers.map((t, i) => {
  const base = 4500 + i * 300
  const bonus = 1200 + i * 200
  return { id: t.id, name: t.nickname, dept: t.dept, base: base.toString(), bonus: bonus.toString(), amount: (base + bonus).toString(), status: i % 4 === 0 ? '待发放' : '已发放' }
})

export const rankingData = Array.from({ length: 8 }, (_, i) => ({
  rank: i + 1, campus: ['总校区', '分校区A', '分校区B', '分校区C'][i % 4] + (i > 3 ? ` ${i}` : ''),
  pendingResource: rnd(0, 50), currentOrders: rnd(0, 30), followExpired: rnd(0, 10),
  invited: rnd(0, 60), promised: rnd(0, 40), hot: rnd(0, 20), visited: rnd(0, 35),
  currentSigned: rnd(0, 25), totalNew: rnd(0, 45), renewals: rnd(0, 30),
  finishedNoRenew: rnd(0, 15), terminated: rnd(0, 5), lost: rnd(0, 8),
  deposit: rnd(0, 20000).toString(), depositRefund: rnd(0, 5000).toString(),
  newRevenue: rnd(0, 80000).toString(), renewRevenue: rnd(0, 60000).toString(),
  refundRevenue: rnd(0, 10000).toString(), actualRevenue: rnd(0, 150000).toString(),
  financeRevenue: rnd(0, 160000).toString(),
}))

export const bonusRecords = teachers.map((t, i) => ({
  id: t.id, name: t.nickname, base: (1000 + i * 100).toString(),
  bonus: (2000 + i * 500).toString(), status: ['已完成', '已完成', '审批中'][i % 3],
}))

export const operationLogs = Array.from({ length: 15 }, (_, i) => ({
  id: i + 1, time: `2026-07-${20 + (i % 8)} ${10 + (i % 8)}:00`, student: students[i % students.length].name,
  action: ['修改学员信息', '新增消课记录', '删除课程评价', '调整班级'][i % 4],
  dataType: ['学员资料', '消课记录', '课程评价', '班级信息'][i % 4], detail: '字段变更详情说明信息。',
  reason: ['信息更正', '正常操作', '家长要求', '教务调整'][i % 4],
  auditor: teachers[i % teachers.length].nickname, campus: ['总校区', '分校区A'][i % 2],
}))

export const knowledgeBase = Array.from({ length: 6 }, (_, i) => ({
  id: i + 1, type: ['产品手册', '话术库', '流程规范'][i % 3], qa: `常见问题解答 ${i + 1}`,
  content: '知识库详细内容说明，涵盖常见场景与标准应答话术。', updateTime: `2026-07-${15 + i}`,
}))

export const teamLibrary = Array.from({ length: 6 }, (_, i) => ({
  id: i + 1, sort: i + 1, type: ['培训资料', '话术模板', '案例分析'][i % 3], starred: i % 2 === 0,
  title: `内部培训素材 ${i + 1}`, permission: ['全员可见', '管理层可见'][i % 2],
  detail: '培训详细内容，包含课件与案例讲解。', teacher: teachers[i % teachers.length].nickname, updateTime: `2026-07-${10 + i}`,
}))

export const documents = Array.from({ length: 8 }, (_, i) => ({
  id: i + 1, category: ['合同', '制度', '模板'][i % 3], starred: i % 3 === 0, pinned: i % 4 === 0,
  title: `文件柜文档 ${i + 1}`, editTime: `2026-07-${10 + i}`,
  publisher: teachers[i % teachers.length].nickname, createTime: `2026-07-${8 + i}`,
}))

export const messages = Array.from({ length: 5 }, (_, i) => ({
  id: i + 1, title: `站内信息通知 ${i + 1}`, sender: teachers[i % teachers.length].nickname,
  time: `2026-07-${25 + i} 09:${10 + i}`, read: i % 2 === 0,
}))

export const revenueTrend = [
  { month: '2月', revenue: 218000, students: 980 },
  { month: '3月', revenue: 245000, students: 1050 },
  { month: '4月', revenue: 268000, students: 1110 },
  { month: '5月', revenue: 298000, students: 1180 },
  { month: '6月', revenue: 312500, students: 1220 },
  { month: '7月', revenue: 328940, students: 1284 },
]
export const attendanceTrend = [62, 78, 55, 90, 84, 40, 30]

export const campusRevenue = ['总校区', '分校区A', '分校区B', '分校区C'].map((campus, i) => {
  const signAmount = 180000 + i * 42000
  const refundAmount = 8000 + i * 1500
  return { id: i + 1, campus, signAmount: signAmount.toString(), refundAmount: refundAmount.toString(), netAmount: (signAmount - refundAmount).toString(), newStudents: 22 + i * 6, renewalRate: (68 + i * 4) + '%' }
})

export const staffRanking = teachers.map((t, i) => ({
  id: t.id, name: t.nickname, role: t.role || '教师',
  performance: (18000 + i * 3200).toString(), attendanceRate: (85 + (i % 10)) + '%', reviewCount: 20 + i * 3,
}))

export const bonusSummary = teachers.map((t, i) => {
  const reviewBonus = 500 + i * 80
  const performanceBonus = 1200 + i * 200
  return { id: t.id, name: t.nickname, dept: ['教务部', '教研部'][i % 2], classHours: 40 + i * 5, reviewBonus: reviewBonus.toString(), performanceBonus: performanceBonus.toString(), totalBonus: (reviewBonus + performanceBonus).toString(), status: i % 3 === 0 ? '待发放' : '已发放' }
})
