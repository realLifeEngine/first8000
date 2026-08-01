<template>
  <div>
    <PageHeader title="仪表盘总览" crumb="总览" subtitle="教育机构运营核心指标一览">
      <template #actions>
        <Button label="导出报表" icon="pi pi-download" outlined @click="exportReport" />
        <Button label="新增学员" icon="pi pi-plus" @click="showAddStudent = true" />
      </template>
    </PageHeader>
    <div class="kpi-grid">
      <KpiCard label="在读学员总数" value="1,284" :delta="4.2" :icon="Users" />
      <KpiCard label="本月实收业绩" value="¥328,940" :delta="6.8" :icon="Wallet" />
      <KpiCard label="本周出勤率" value="91.5%" :delta="-1.3" :icon="CalendarCheck" />
      <KpiCard label="待评课堂数" value="18" :delta="null" :icon="ClipboardCheck" accent="var(--color-warning)" />
    </div>
    <div class="content-grid">
      <div class="chart-card"><div class="card-head"><h3>营收与学员趋势</h3></div><div ref="revenueChartEl" class="chart-el"></div></div>
      <div class="chart-card"><div class="card-head"><h3>本周出勤分布</h3></div><div ref="attendanceChartEl" class="chart-el"></div></div>
    </div>
    <div class="content-grid">
      <div class="list-card">
        <div class="card-head"><h3>待办工作计划</h3><router-link to="/app/oa/plans" class="link">查看全部</router-link></div>
        <ul class="todo-list" role="list">
          <li v-for="p in workPlans.slice(0,5)" :key="p.id" class="todo-item" @click="openPlan(p)">
            <div class="todo-priority" :class="'p-' + p.priority"></div>
            <div class="todo-body"><p class="todo-title">{{ p.title }}</p><p class="todo-meta">{{ p.owner }} · 截止 {{ p.deadline }}</p></div>
            <StatusTag :value="p.read" />
          </li>
        </ul>
      </div>
      <div class="list-card">
        <div class="card-head"><h3>最新公文通知</h3><router-link to="/app/oa/notices" class="link">查看全部</router-link></div>
        <ul class="todo-list" role="list">
          <li v-for="n in notices" :key="n.id" class="todo-item" @click="openNotice(n)">
            <FileText :size="16" class="notice-icon" />
            <div class="todo-body"><p class="todo-title">{{ n.title }}</p><p class="todo-meta">{{ n.publisher }} · {{ n.createTime }}</p></div>
            <StatusTag :value="n.status" />
          </li>
        </ul>
      </div>
    </div>
    <RecordDialog v-model:visible="showAddStudent" title="新增学员" confirm-label="保存并添加" @confirm="confirmAddStudent">
      <div class="form-grid">
        <div class="field"><label>学员姓名</label><InputText v-model="newStudent.name" placeholder="请输入姓名" /></div>
        <div class="field"><label>性别</label><SelectButton v-model="newStudent.gender" :options="['男','女']" /></div>
        <div class="field"><label>年龄</label><InputNumber v-model="newStudent.age" :min="1" :max="99" /></div>
        <div class="field"><label>业务状态</label><Dropdown v-model="newStudent.status" :options="statuses" placeholder="请选择" /></div>
        <div class="field full"><label>联系电话</label><InputText v-model="newStudent.phone" placeholder="请输入联系电话" /></div>
        <div class="field full"><label>备注</label><Textarea v-model="newStudent.remark" rows="3" autoResize /></div>
      </div>
    </RecordDialog>
    <Dialog v-model:visible="showPlanDialog" modal header="工作计划详情" :style="{ width: '520px' }">
      <div v-if="activePlan" class="detail-view">
        <div class="detail-row"><span>标题</span><strong>{{ activePlan.title }}</strong></div>
        <div class="detail-row"><span>负责人</span><span>{{ activePlan.owner }}</span></div>
        <div class="detail-row"><span>优先级</span><StatusTag :value="activePlan.priority" /></div>
        <div class="detail-row"><span>截止时间</span><span>{{ activePlan.deadline }}</span></div>
        <div class="detail-row"><span>进度</span><ProgressBar :value="Number(activePlan.progress)" /></div>
        <div class="detail-row"><span>反馈</span><span>{{ activePlan.feedback }}</span></div>
      </div>
      <template #footer><Button label="关闭" @click="showPlanDialog = false" /></template>
    </Dialog>
    <Dialog v-model:visible="showNoticeDialog" modal header="公文详情" :style="{ width: '560px' }">
      <div v-if="activeNotice" class="detail-view">
        <h4 class="notice-title">{{ activeNotice.title }}</h4>
        <p class="notice-meta">{{ activeNotice.publisher }} · {{ activeNotice.createTime }}</p>
        <p class="notice-content">{{ activeNotice.content }}</p>
      </div>
      <template #footer><Button label="关闭" @click="showNoticeDialog = false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Users, Wallet, CalendarCheck, ClipboardCheck, FileText } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import KpiCard from '../components/KpiCard.vue'
import StatusTag from '../components/StatusTag.vue'
import RecordDialog from '../components/RecordDialog.vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import SelectButton from 'primevue/selectbutton'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import ProgressBar from 'primevue/progressbar'
import { useToast } from 'primevue/usetoast'
import { workPlans as workPlansApi, notices as noticesApi } from '../api/oa'
import { createStudent } from '../api/students'
const toast = useToast()
const statuses = ['意向', '正常', '停课', '结课', '流失']
const workPlans = ref([])
const notices = ref([])
// No revenue/attendance time-series endpoint exists yet on the backend;
// these charts remain illustrative until Batch 8 adds a reporting API.
const revenueTrend = [
  { month: '1月', revenue: 210000 }, { month: '2月', revenue: 198000 }, { month: '3月', revenue: 245000 },
  { month: '4月', revenue: 267000 }, { month: '5月', revenue: 289000 }, { month: '6月', revenue: 328940 },
]
const attendanceTrend = [92, 88, 95, 90, 93, 85, 91]

async function fetchDashboardData() {
  try {
    const [plansRes, noticesRes] = await Promise.all([
      workPlansApi.list({ page: 1, page_size: 10 }),
      noticesApi.list({ page: 1, page_size: 10 }),
    ])
    workPlans.value = plansRes.items
    notices.value = noticesRes.items
  } catch (err) {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取仪表盘数据', life: 3000 })
  }
}
fetchDashboardData()
const revenueChartEl = ref(null)
const attendanceChartEl = ref(null)
const showAddStudent = ref(false)
const newStudent = ref({ name: '', gender: '男', age: 8, status: '意向', phone: '', remark: '' })
const showPlanDialog = ref(false)
const activePlan = ref(null)
function openPlan(p) { activePlan.value = p; showPlanDialog.value = true }
const showNoticeDialog = ref(false)
const activeNotice = ref(null)
function openNotice(n) { activeNotice.value = n; showNoticeDialog.value = true }
async function confirmAddStudent() {
  try {
    await createStudent(newStudent.value)
    showAddStudent.value = false
    toast.add({ severity: 'success', summary: '添加成功', detail: `学员 ${newStudent.value.name || '新学员'} 已加入系统`, life: 3000 })
    newStudent.value = { name: '', gender: '男', age: 8, status: '意向', phone: '', remark: '' }
  } catch (err) {
    toast.add({ severity: 'error', summary: '添加失败', detail: err.response?.data?.detail || '请稍后重试', life: 3000 })
  }
}
function exportReport() { toast.add({ severity: 'info', summary: '导出中', detail: '报表已生成，正在下载...', life: 2500 }) }
function renderCharts() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
  const textColor = isDark ? '#8b959e' : '#5c6570'
  const primary = isDark ? '#4bab9f' : '#0e6b62'
  const svgNS = 'http://www.w3.org/2000/svg'
  if (revenueChartEl.value) {
    revenueChartEl.value.innerHTML = ''
    const max = Math.max(...revenueTrend.map(d => d.revenue))
    const w = revenueChartEl.value.clientWidth || 480, h = 220, padding = 30
    const svg = document.createElementNS(svgNS, 'svg')
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.setAttribute('width', '100%'); svg.setAttribute('height', h)
    const stepX = (w - padding * 2) / (revenueTrend.length - 1)
    const points = revenueTrend.map((d, i) => [padding + i * stepX, h - padding - (d.revenue / max) * (h - padding * 2)])
    const path = points.map((p, i) => (i === 0 ? 'M' : 'L') + p[0] + ',' + p[1]).join(' ')
    const areaPath = path + ` L${points[points.length - 1][0]},${h - padding} L${points[0][0]},${h - padding} Z`
    const area = document.createElementNS(svgNS, 'path'); area.setAttribute('d', areaPath); area.setAttribute('fill', primary); area.setAttribute('opacity', '0.12'); svg.appendChild(area)
    const line = document.createElementNS(svgNS, 'path'); line.setAttribute('d', path); line.setAttribute('fill', 'none'); line.setAttribute('stroke', primary); line.setAttribute('stroke-width', '2.5'); svg.appendChild(line)
    points.forEach((p, i) => {
      const c = document.createElementNS(svgNS, 'circle'); c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', '4'); c.setAttribute('fill', primary); svg.appendChild(c)
      const t = document.createElementNS(svgNS, 'text'); t.setAttribute('x', p[0]); t.setAttribute('y', h - 8); t.setAttribute('text-anchor', 'middle'); t.setAttribute('font-size', '11'); t.setAttribute('fill', textColor); t.textContent = revenueTrend[i].month; svg.appendChild(t)
    })
    revenueChartEl.value.appendChild(svg)
  }
  if (attendanceChartEl.value) {
    attendanceChartEl.value.innerHTML = ''
    const days = ['一', '二', '三', '四', '五', '六', '日']
    const max = Math.max(...attendanceTrend)
    const w = attendanceChartEl.value.clientWidth || 480, h = 220
    const barW = (w / attendanceTrend.length) * 0.5, gap = (w / attendanceTrend.length)
    const svg = document.createElementNS(svgNS, 'svg')
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.setAttribute('width', '100%'); svg.setAttribute('height', h)
    attendanceTrend.forEach((v, i) => {
      const barH = (v / max) * (h - 50), x = i * gap + (gap - barW) / 2, y = h - 30 - barH
      const rect = document.createElementNS(svgNS, 'rect'); rect.setAttribute('x', x); rect.setAttribute('y', y); rect.setAttribute('width', barW); rect.setAttribute('height', barH); rect.setAttribute('rx', '4'); rect.setAttribute('fill', primary); rect.setAttribute('opacity', 0.85); svg.appendChild(rect)
      const t = document.createElementNS(svgNS, 'text'); t.setAttribute('x', x + barW / 2); t.setAttribute('y', h - 10); t.setAttribute('text-anchor', 'middle'); t.setAttribute('font-size', '11'); t.setAttribute('fill', textColor); t.textContent = days[i]; svg.appendChild(t)
    })
    attendanceChartEl.value.appendChild(svg)
  }
}
onMounted(() => { nextTick(renderCharts); window.addEventListener('resize', renderCharts) })
</script>
<style scoped>
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6); }
.content-grid { display: grid; grid-template-columns: 1fr; gap: var(--space-4); margin-bottom: var(--space-6); }
@media (min-width: 900px) { .content-grid { grid-template-columns: 1.3fr 1fr; } }
.chart-card, .list-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-5); box-shadow: var(--shadow-sm); }
.card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-4); }
.card-head h3 { font-size: var(--text-base); font-weight: 600; }
.link { font-size: var(--text-sm); color: var(--color-primary); text-decoration: none; }
.chart-el { width: 100%; min-height: 220px; }
.todo-list { display: flex; flex-direction: column; gap: var(--space-1); }
.todo-item { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-3); border-radius: var(--radius-md); cursor: pointer; }
.todo-item:hover { background: var(--color-surface-offset); }
.todo-priority { width: 6px; height: 32px; border-radius: var(--radius-full); background: var(--color-text-faint); flex-shrink: 0; }
.todo-priority.p-高 { background: var(--color-error); }
.todo-priority.p-中 { background: var(--color-warning); }
.todo-priority.p-低 { background: var(--color-success); }
.notice-icon { color: var(--color-text-faint); flex-shrink: 0; }
.todo-body { flex: 1; min-width: 0; }
.todo-title { font-size: var(--text-sm); font-weight: 500; }
.todo-meta { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: 2px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.detail-view { display: flex; flex-direction: column; gap: var(--space-3); }
.detail-row { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); font-size: var(--text-sm); }
.detail-row span:first-child { color: var(--color-text-muted); }
.notice-title { font-size: var(--text-lg); margin-bottom: var(--space-2); }
.notice-meta { font-size: var(--text-xs); color: var(--color-text-faint); margin-bottom: var(--space-3); }
.notice-content { font-size: var(--text-sm); line-height: 1.7; }
</style>
