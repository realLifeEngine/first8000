<template>
  <div>
    <PageHeader title="班级管理" crumb="教务管理 > 班级管理" subtitle="维护班级排课、容量与主题信息">
      <template #actions><Button v-if="auth.can('class:manage')" label="新增班级" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" :loading="loading" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <template #empty>
          <div class="empty-state"><i class="pi pi-calendar" /><span>当前暂无班级数据。</span></div>
        </template>
        <Column field="name" header="班级名称" sortable />
        <Column field="branchName" header="隶属校区" sortable />
        <Column field="teacherName" header="授课老师" sortable />
        <Column field="courseName" header="课程产品" sortable />
        <Column field="scheduleDate" header="上课日期" />
        <Column field="scheduleTime" header="上课时段" />
        <Column field="capacityDisplay" header="班容情况" sortable>
          <template #body="{ data }">
            <div class="capacity-cell"><ProgressBar :value="capacityPct(data)" :showValue="false" style="width:80px;height:8px" /><span class="tabular">{{ data.capacityDisplay }}</span></div>
          </template>
        </Column>
        <Column field="status" header="状态" sortable><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
        <Column header="管理" style="width:110px">
          <template #body="{ data }">
            <div class="row-actions">
              <button class="icon-action" type="button" aria-label="编辑班级" @click="openEdit(data)"><Pencil :size="15" /></button>
              <button class="icon-action" type="button" aria-label="查看班级学员" @click="viewStudents(data)"><Users :size="15" /></button>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑班级' : '新增班级'" width="640px" @confirm="save">
      <div class="form-grid">
        <div class="field full"><label>班级名称</label><InputText v-model="form.name" /></div>
        <div class="field"><label>隶属校区</label><Dropdown v-model="form.branch_id" :options="branchOptions" optionLabel="label" optionValue="value" placeholder="请选择校区" /></div>
        <div class="field"><label>授课老师</label><Dropdown v-model="form.teacher_id" :options="teacherOptions" optionLabel="label" optionValue="value" placeholder="请选择老师" showClear /></div>
        <div class="field"><label>课程产品</label><Dropdown v-model="form.course_product_id" :options="courseOptions" optionLabel="label" optionValue="value" placeholder="请选择课程" showClear /></div>
        <div class="field"><label>班级状态</label><Dropdown v-model="form.status" :options="classStatuses" placeholder="请选择状态" /></div>
        <div class="field"><label>已报人数</label><InputText v-model="form.enrolled" /></div>
        <div class="field"><label>班级容量</label><InputText v-model="form.capacity" /></div>
        <div class="field full"><label>排课安排</label>
          <div class="schedule-row">
            <MultiSelect
              v-model="form.schedule_days"
              :options="weekdayOptions"
              optionLabel="label"
              optionValue="value"
              display="chip"
              appendTo="body"
              placeholder="选择上课星期（可多选）"
              style="flex:1"
            />
            <Calendar
              v-model="form.schedule_time_start"
              timeOnly
              showIcon
              hourFormat="24"
              appendTo="body"
              placeholder="开始时间"
              style="flex:1"
            />
            <span class="time-sep">-</span>
            <Calendar
              v-model="form.schedule_time_end"
              timeOnly
              showIcon
              hourFormat="24"
              appendTo="body"
              placeholder="结束时间"
              style="flex:1"
            />
          </div>
          <small v-if="editing && form.schedule && !form.schedule_days?.length" class="muted">
            当前记录为旧排课格式：{{ form.schedule }}。若要更新，请重新选择日期和时间。
          </small>
        </div>
      </div>
    </RecordDialog>
    <Dialog v-model:visible="showStudents" modal header="班级学员列表" :style="{ width: '520px' }">
      <p class="muted" v-if="activeClass">{{ activeClass.name }} · {{ activeClass.branchName }} · {{ activeClass.teacherName }}</p>
      <div class="assign-row">
        <Dropdown v-model="selectedStudentId" :options="availableStudentOptions" optionLabel="label" optionValue="value" placeholder="选择学员加入班级" showClear style="flex:1" />
        <Button label="添加" size="small" @click="assignSelectedStudent" :disabled="!selectedStudentId || studentsLoading" />
      </div>
      <ul class="student-mini-list" role="list">
        <li v-for="s in classStudents" :key="s.id">
          <Avatar :label="s.name.charAt(0)" shape="circle" size="normal" />
          <span>{{ s.name }}</span>
          <StatusTag :value="s.status" />
          <button class="icon-action danger" type="button" aria-label="移出班级" @click="removeStudent(s)"><i class="pi pi-times" /></button>
        </li>
      </ul>
      <p v-if="!classStudents.length && !studentsLoading" class="muted">当前班级所在校区暂无可展示的学员。</p>
      <template #footer><Button label="关闭" @click="showStudents = false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { Pencil, Users } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import MultiSelect from 'primevue/multiselect'
import ProgressBar from 'primevue/progressbar'
import Dialog from 'primevue/dialog'
import Avatar from 'primevue/avatar'
import { useToast } from 'primevue/usetoast'
import {
  listClasses,
  createClass,
  updateClass,
  listClassStudents,
  listAvailableClassStudents,
  listCourseProducts,
  assignStudentToClass,
  removeStudentFromClass,
} from '../../api/school'
import { listBranches } from '../../api/branches'
import { listStaff } from '../../api/staff'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])
const loading = ref(false)
const branches = ref([])
const teachers = ref([])
const courses = ref([])
const classStatuses = ['进行中', '已结束', '待开班']
const weekdayOptions = [
  { label: '周一', value: '周一' },
  { label: '周二', value: '周二' },
  { label: '周三', value: '周三' },
  { label: '周四', value: '周四' },
  { label: '周五', value: '周五' },
  { label: '周六', value: '周六' },
  { label: '周日', value: '周日' },
]

function defaultForm() {
  return {
    name: '',
    branch_id: auth.user?.branchId || '',
    teacher_id: null,
    course_product_id: null,
    enrolled: '0',
    capacity: '15',
    schedule: '',
    schedule_days: [],
    schedule_time_start: null,
    schedule_time_end: null,
    status: '进行中',
  }
}

function parseScheduleForForm(schedule) {
  const text = String(schedule || '').trim()
  if (!text) return { schedule_days: [], schedule_time_start: null, schedule_time_end: null }

  const dayMatches = text.match(/周[一二三四五六日天]/g) || []
  const normalizeDay = (day) => (day === '周天' ? '周日' : day)
  const uniqueDays = [...new Set(dayMatches.map(normalizeDay))]
  const rangeMatch = text.match(/(\d{1,2}):(\d{2})(?:\s*-\s*(\d{1,2}):(\d{2}))?/)

  const schedule_time_start = rangeMatch
    ? new Date(2000, 0, 1, Number(rangeMatch[1]), Number(rangeMatch[2]))
    : null
  const schedule_time_end = rangeMatch && rangeMatch[3] != null && rangeMatch[4] != null
    ? new Date(2000, 0, 1, Number(rangeMatch[3]), Number(rangeMatch[4]))
    : null

  return { schedule_days: uniqueDays, schedule_time_start, schedule_time_end }
}

function pad2(value) {
  return String(value).padStart(2, '0')
}

function buildScheduleText() {
  const days = Array.isArray(form.value.schedule_days) ? form.value.schedule_days : []
  const start = form.value.schedule_time_start
  const end = form.value.schedule_time_end

  if (days.length && start && end) {
    const dayText = days.join('/')
    const startText = `${pad2(start.getHours())}:${pad2(start.getMinutes())}`
    const endText = `${pad2(end.getHours())}:${pad2(end.getMinutes())}`
    return `${dayText} ${startText}-${endText}`
  }
  if (days.length && start) {
    const dayText = days.join('/')
    const timeText = `${pad2(start.getHours())}:${pad2(start.getMinutes())}`
    return `${dayText} ${timeText}`
  }
  if (days.length) {
    return days.join('/')
  }
  if (editing.value && form.value.schedule) {
    return form.value.schedule
  }
  return null
}

function splitSchedule(schedule) {
  const text = String(schedule || '').trim()
  const match = text.match(/^(.*?)(\d{1,2}:\d{2}.*)$/)
  if (!match) return { scheduleDate: text, scheduleTime: '' }
  return { scheduleDate: match[1].trim(), scheduleTime: match[2].trim() }
}

function mapClassRow(item) {
  const branch = branches.value.find((entry) => entry.id === item.branch_id)
  const teacher = teachers.value.find((entry) => entry.id === item.teacher_id)
  const course = courses.value.find((entry) => entry.id === item.course_product_id)
  return {
    ...item,
    branchName: branch?.name?.trim() || '-',
    teacherName: teacher?.nickname || teacher?.name || '-',
    courseName: course?.name || '-',
    capacityDisplay: `${Number(item.enrolled || 0)}/${Number(item.capacity || 0)}`,
    ...splitSchedule(item.schedule),
  }
}

const branchOptions = ref([])
const teacherOptions = ref([])
const courseOptions = ref([])

function refreshOptions() {
  branchOptions.value = branches.value.map((item) => ({ label: item.name.trim(), value: item.id }))
  teacherOptions.value = teachers.value.map((item) => ({ label: item.nickname || item.name, value: item.id }))
  courseOptions.value = courses.value.map((item) => ({ label: item.name, value: item.id }))
}

async function loadMeta() {
  const [branchResp, staffResp, courseResp] = await Promise.all([
    listBranches({ page: 1, page_size: 100 }),
    listStaff({ page: 1, page_size: 100 }),
    listCourseProducts({ page: 1, page_size: 100 }),
  ])
  branches.value = branchResp.items || []
  teachers.value = (staffResp.items || []).filter((item) => item.is_active)
  courses.value = courseResp
  refreshOptions()
}

async function loadClasses() {
  loading.value = true
  try {
    const data = await listClasses()
    list.value = data.map(mapClassRow)
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await loadMeta()
    await loadClasses()
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  }
})

function capacityPct(row) {
  const a = Number(row?.enrolled || 0)
  const b = Number(row?.capacity || 0)
  if (!Number.isFinite(a) || !Number.isFinite(b) || b <= 0) return 0
  return Math.max(0, Math.min(100, Math.round((a / b) * 100)))
}
const showEditor = ref(false)
const editing = ref(false)
const form = ref(defaultForm())
function openCreate() { editing.value = false; form.value = defaultForm(); showEditor.value = true }
function openEdit(row) {
  const parsedSchedule = parseScheduleForForm(row.schedule)
  editing.value = true
  form.value = {
    id: row.id,
    name: row.name,
    branch_id: row.branch_id,
    teacher_id: row.teacher_id,
    course_product_id: row.course_product_id,
    enrolled: String(Number(row.enrolled || 0)),
    capacity: String(Number(row.capacity || 0)),
    schedule: row.schedule || '',
    schedule_days: parsedSchedule.schedule_days,
    schedule_time_start: parsedSchedule.schedule_time_start,
    schedule_time_end: parsedSchedule.schedule_time_end,
    status: row.status || '进行中',
  }
  showEditor.value = true
}

function buildPayload() {
  return {
    name: form.value.name,
    branch_id: form.value.branch_id,
    teacher_id: form.value.teacher_id || null,
    course_product_id: form.value.course_product_id || null,
    enrolled: Number(form.value.enrolled || 0),
    capacity: Number(form.value.capacity || 0),
    schedule: buildScheduleText(),
    status: form.value.status,
  }
}

async function save() {
  try {
    if (editing.value) {
      await updateClass(form.value.id, buildPayload())
    } else {
      await createClass(buildPayload())
    }
    await loadClasses()
    toast.add({ severity: 'success', summary: editing.value ? '更新成功' : '新增成功', life: 2500 })
    showEditor.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: '操作失败', detail: e.message, life: 3000 })
  }
}

const showStudents = ref(false)
const activeClass = ref(null)
const studentsLoading = ref(false)
const classStudents = ref([])
const availableStudents = ref([])
const selectedStudentId = ref(null)

const availableStudentOptions = ref([])

function refreshAvailableStudentOptions() {
  availableStudentOptions.value = availableStudents.value.map((student) => {
    const classLabel = student.classInfo ? `（当前: ${student.classInfo}）` : ''
    return { label: `${student.name}${classLabel}`, value: student.id }
  })
}

async function reloadClassStudents(classId) {
  const [assigned, available] = await Promise.all([
    listClassStudents(classId),
    listAvailableClassStudents(classId),
  ])
  classStudents.value = assigned
  availableStudents.value = available
  refreshAvailableStudentOptions()
}

async function viewStudents(row) {
  activeClass.value = row
  showStudents.value = true
  selectedStudentId.value = null
  studentsLoading.value = true
  try {
    await reloadClassStudents(row.id)
  } catch (e) {
    classStudents.value = []
    availableStudents.value = []
    refreshAvailableStudentOptions()
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    studentsLoading.value = false
  }
}

async function assignSelectedStudent() {
  if (!selectedStudentId.value || !activeClass.value) return
  studentsLoading.value = true
  try {
    const result = await assignStudentToClass(activeClass.value.id, selectedStudentId.value)
    if (!result.ok) {
      toast.add({ severity: 'warn', summary: '无法添加', detail: result.detail || '请稍后重试', life: 2500 })
      return
    }
    selectedStudentId.value = null
    await Promise.all([reloadClassStudents(activeClass.value.id), loadClasses()])
    toast.add({ severity: 'success', summary: '已添加到班级', life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: '操作失败', detail: e.message, life: 3000 })
  } finally {
    studentsLoading.value = false
  }
}

async function removeStudent(student) {
  if (!activeClass.value) return
  studentsLoading.value = true
  try {
    const result = await removeStudentFromClass(activeClass.value.id, student.id)
    if (!result.ok) {
      toast.add({ severity: 'warn', summary: '无法移除', detail: result.detail || '请稍后重试', life: 2500 })
      return
    }
    await Promise.all([reloadClassStudents(activeClass.value.id), loadClasses()])
    toast.add({ severity: 'success', summary: '已移出班级', life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: '操作失败', detail: e.message, life: 3000 })
  } finally {
    studentsLoading.value = false
  }
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.capacity-cell { display: flex; align-items: center; gap: var(--space-2); }
.row-actions { display: flex; gap: var(--space-2); }
.icon-action { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: var(--radius-md); color: var(--color-text-muted); }
.icon-action:hover { background: var(--color-surface-offset); color: var(--color-primary); }
.icon-action.danger:hover { background: var(--color-error-highlight); color: var(--color-error); }
.empty-state { display: flex; align-items: center; justify-content: center; gap: var(--space-2); padding: var(--space-5); color: var(--color-text-muted); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.schedule-row { display: flex; align-items: center; gap: var(--space-3); }
.time-sep { color: var(--color-text-muted); font-weight: 600; }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); margin-bottom: var(--space-3); }
.assign-row { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3); }
.student-mini-list { display: flex; flex-direction: column; gap: var(--space-2); }
.student-mini-list li { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2); border-radius: var(--radius-md); }
.student-mini-list li:hover { background: var(--color-surface-offset); }
.student-mini-list li span { flex: 1; }
</style>
