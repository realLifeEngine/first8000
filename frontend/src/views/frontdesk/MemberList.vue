<template>
  <div>
    <PageHeader title="会员管理" crumb="前台业务 > 会员管理" subtitle="学员全生命周期信息与业务指标">
      <template #actions>
        <Button v-if="auth.can('student:search')" label="高级搜索" icon="pi pi-filter" outlined @click="showFilter = true" />
        <Button v-if="auth.can('student:create')" style="color: white;" iconPos="left" label="新增学员" icon="pi pi-plus" @click="openCreate" />
      </template>
    </PageHeader>

    <div class="summary-grid">
      <Card class="summary-card accent">
        <template #content>
          <div class="summary-title">累计学员</div>
          <div class="summary-value">{{ summary.total }}</div>
          <div class="summary-meta">已录入系统的学员总量</div>
        </template>
      </Card>
      <Card class="summary-card">
        <template #content>
          <div class="summary-title">意向/正常/停课</div>
          <div class="summary-value">{{ summary.active }}</div>
          <div class="summary-meta">重点跟进中的学员数量</div>
        </template>
      </Card>
      <Card class="summary-card">
        <template #content>
          <div class="summary-title">准时率达标</div>
          <div class="summary-value">{{ summary.onTime }}</div>
          <div class="summary-meta">准时出勤率 ≥ 85% 的学员</div>
        </template>
      </Card>
      <Card class="summary-card">
        <template #content>
          <div class="summary-title">累计收款</div>
          <div class="summary-value">¥{{ summary.revenue.toLocaleString() }}</div>
          <div class="summary-meta">当前筛选结果汇总</div>
        </template>
      </Card>
    </div>

    <div class="toolbar">
      <div class="filter-chip-group">
        <SelectButton v-model="statusFilter" :options="['全部', ...statuses]" class="status-toggle" />
      </div>
      <span class="spacer"></span>
      <div class="toolbar-actions">
        <Button class="reset-filter-btn" label="重置筛选" icon="pi pi-refresh" text severity="secondary" @click="resetFilters" />
        <div class="search-shell">
          <i class="pi pi-search search-icon" aria-hidden="true"></i>
          <InputText v-model="search" placeholder="搜索学员姓名..." class="search-input" />
        </div>
      </div>
    </div>

    <div class="table-card">
      <DataTable
        :value="list"
        :loading="loading"
        :lazy="true"
        paginator
        :rows="rows"
        :first="first"
        :totalRecords="totalRecords"
        :rowsPerPageOptions="[8, 12, 20]"
        :sortField="sortField"
        :sortOrder="sortOrder"
        dataKey="id"
        responsiveLayout="scroll"
        stripedRows
        showGridlines
        rowHover
        removableSort
        currentPageReportTemplate="显示 {first} 至 {last} / {totalRecords} 条"
        @page="handlePage"
        @sort="handleSort"
        @row-click="openDetail($event.data)"
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-search" />
            <span>暂无匹配的学员记录，请调整筛选条件。</span>
          </div>
        </template>
        <Column field="name" header="学员姓名" sortable>
          <template #body="{ data }">
            <div class="name-cell">
              <Avatar :label="data.name.charAt(0)" shape="circle" size="normal" />
              <div>
                <div class="name-text">{{ data.name }}</div>
                <div class="name-meta">{{ data.phone }}</div>
              </div>
            </div>
          </template>
        </Column>
        <Column field="gender" header="性别" sortable />
        <Column field="age" header="年龄" sortable />
        <Column field="status" header="业务状态" sortable>
          <template #body="{ data }"><StatusTag :value="data.status" /></template>
        </Column>
        <Column field="classInfo" header="班级信息" sortable />
        <Column field="totalPaid" header="总收款" sortable>
          <template #body="{ data }"><span class="tabular">¥{{ Number(data.totalPaid).toLocaleString() }}</span></template>
        </Column>
        <Column field="consumed" header="消课" sortable />
        <Column field="onTimeRate" header="准时出勤" sortable>
          <template #body="{ data }">
            <div class="attendance-cell">
              <span>{{ data.onTimeRate || '0%' }}</span>
              <ProgressBar :value="getOnTimeRateValue(data)" :showValue="false" />
            </div>
          </template>
        </Column>
        <Column field="counselor" header="学管老师" sortable />
        <Column header="管理" style="width:110px">
          <template #body="{ data }">
            <div class="row-actions" @click.stop>
              <button v-if="auth.can('student:edit')" class="icon-action" @click="openEdit(data)" aria-label="编辑"><Pencil :size="15" /></button>
              <button v-if="auth.can('student:delete')" class="icon-action danger" @click="confirmDelete(data)" aria-label="删除"><Trash2 :size="15" /></button>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <RecordDialog v-model:visible="showFilter" title="按条件筛选" width="640px" confirm-label="应用筛选" @confirm="applyFilters">
      <div class="form-grid">
        <div class="field"><label>学员姓名</label><InputText v-model="filterForm.name" placeholder="请输入" /></div>
        <div class="field"><label>业务状态</label><Dropdown v-model="filterForm.status" :options="['全部', ...statuses]" /></div>
        <div class="field"><label>班级信息</label><InputText v-model="filterForm.classInfo" placeholder="请输入班级" /></div>
        <div class="field"><label>学管老师</label><InputText v-model="filterForm.counselor" placeholder="请输入老师姓名" /></div>
      </div>
    </RecordDialog>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑学员信息' : '新增学员'" width="640px" @confirm="saveStudent">
      <div class="form-grid">
        <div class="field"><label>学员姓名</label><InputText v-model="form.name" placeholder="请输入姓名" /></div>
        <div class="field"><label>性别</label><SelectButton v-model="form.gender" :options="['男','女']" /></div>
        <div class="field"><label>年龄</label><InputNumber v-model="form.age" :min="1" :max="99" /></div>
        <div class="field"><label>业务状态</label><Dropdown v-model="form.status" :options="statuses" /></div>
        <div class="field"><label>班级信息</label><Dropdown v-model="form.classInfo" :options="classOptions" optionLabel="label" optionValue="value" placeholder="请选择班级" :loading="classOptionsLoading" showClear filter /></div>
        <div class="field"><label>学管老师</label><InputText v-model="form.counselor" /></div>
        <div class="field full"><label>联系电话</label><InputText v-model="form.phone" /></div>
        <div class="field full"><label>备注</label><Textarea v-model="form.remark" rows="3" autoResize /></div>
      </div>
    </RecordDialog>
    <Dialog v-model:visible="showDetail" modal header="学员详情" :style="{ width: '720px' }" :breakpoints="{ '960px': '92vw' }">
      <div v-if="activeStudent" class="detail-panel">
        <div class="detail-header">
          <Avatar :label="activeStudent.name.charAt(0)" shape="circle" size="xlarge" />
          <div><h3>{{ activeStudent.name }}</h3><p class="muted">{{ activeStudent.gender }} · {{ activeStudent.age }}岁 · {{ activeStudent.classInfo }}</p></div>
          <StatusTag :value="activeStudent.status" />
        </div>
        <TabView>
          <TabPanel header="基本情况">
            <div class="detail-grid">
              <div><span class="muted">常规课时</span><p class="tabular">{{ activeStudent.regular }}</p></div>
              <div><span class="muted">赠课</span><p class="tabular">{{ activeStudent.gift }}</p></div>
              <div><span class="muted">其他</span><p class="tabular">{{ activeStudent.other }}</p></div>
              <div><span class="muted">储值</span><p class="tabular">¥{{ activeStudent.stored }}</p></div>
              <div><span class="muted">联系电话</span><p>{{ activeStudent.phone }}</p></div>
              <div><span class="muted">学管老师</span><p>{{ activeStudent.counselor }}</p></div>
            </div>
          </TabPanel>
          <TabPanel header="消课数据">
            <div class="detail-grid">
              <div><span class="muted">总收款</span><p class="tabular">¥{{ Number(activeStudent.totalPaid).toLocaleString() }}</p></div>
              <div><span class="muted">消课(课时)</span><p class="tabular">{{ activeStudent.consumed }}</p></div>
              <div><span class="muted">缺勤</span><p class="tabular">{{ activeStudent.absence }}</p></div>
              <div><span class="muted">准时出勤</span><p class="tabular">{{ activeStudent.onTimeRate }}</p></div>
              <div><span class="muted">上次消课</span><p>{{ activeStudent.lastConsume }}</p></div>
              <div><span class="muted">耗课频率</span><p>{{ activeStudent.consumeFreq }}</p></div>
            </div>
          </TabPanel>
          <TabPanel header="沟通记录">
            <div class="detail-grid">
              <div><span class="muted">上次沟通</span><p>{{ activeStudent.lastContact }}</p></div>
              <div><span class="muted">下次联系</span><p>{{ activeStudent.nextContact }}</p></div>
              <div><span class="muted">课评浏览</span><p class="tabular">{{ activeStudent.reviewViews }}</p></div>
              <div><span class="muted">浏览率</span><p class="tabular">{{ activeStudent.viewRate }}</p></div>
            </div>
          </TabPanel>
        </TabView>
      </div>
      <template #footer><Button label="编辑信息" outlined @click="editFromDetail" /><Button label="关闭" @click="showDetail = false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref, watch, onMounted } from 'vue'
import { Pencil, Trash2 } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import SelectButton from 'primevue/selectbutton'
import Textarea from 'primevue/textarea'
import Avatar from 'primevue/avatar'
import Dialog from 'primevue/dialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Card from 'primevue/card'
import ProgressBar from 'primevue/progressbar'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { listStudentsPage, createStudent, updateStudent, deleteStudent, listStudentClassOptions } from '../../api/students'
import { useAuthStore } from '../../stores/auth'

const toast = useToast()
const confirm = useConfirm()
const auth = useAuthStore()
const statuses = ['意向', '正常', '停课', '结课', '流失']
const list = ref([])
const loading = ref(false)
const totalRecords = ref(0)
const rows = ref(8)
const first = ref(0)
const currentPage = ref(1)
const search = ref('')
const statusFilter = ref('全部')
const appliedFilters = ref({ name: '', status: '全部', classInfo: '', counselor: '' })
const showFilter = ref(false)
const filterForm = ref({ name: '', status: '全部', classInfo: '', counselor: '' })
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ name: '', gender: '男', age: 8, status: '意向', classInfo: '', counselor: '', phone: '', remark: '' })
const classOptions = ref([])
const classOptionsLoading = ref(false)
const sortField = ref(null)
const sortOrder = ref(null)
const summary = ref({ total: 0, active: 0, onTime: 0, revenue: 0 })
let searchTimer = null
let skipNextStatusReload = false
let skipNextSearchReload = false

function getOnTimeRateValue(student) {
  const rawRate = student?.onTimeRate
  if (!rawRate) return 0
  return Number(String(rawRate).replace('%', '')) || 0
}

function buildQueryParams(page = currentPage.value, pageSize = rows.value) {
  return {
    page,
    pageSize,
    search: search.value.trim() || undefined,
    name: appliedFilters.value.name || undefined,
    status: statusFilter.value !== '全部' ? statusFilter.value : undefined,
    classInfo: appliedFilters.value.classInfo || undefined,
    counselor: appliedFilters.value.counselor || undefined,
    sortField: sortField.value || undefined,
    sortOrder: sortOrder.value || undefined,
  }
}

async function loadStudents({ page = currentPage.value, pageSize = rows.value } = {}) {
  loading.value = true
  try {
    const data = await listStudentsPage(buildQueryParams(page, pageSize))
    if (!data.items.length && data.total > 0 && page > 1) {
      const previousPage = page - 1
      currentPage.value = previousPage
      first.value = (previousPage - 1) * pageSize
      await loadStudents({ page: previousPage, pageSize })
      return
    }
    list.value = data.items
    totalRecords.value = data.total
    rows.value = data.pageSize
    currentPage.value = data.page
    first.value = (data.page - 1) * data.pageSize
    summary.value = {
      total: data.summary?.total ?? data.total ?? 0,
      active: data.summary?.active ?? 0,
      onTime: data.summary?.onTime ?? 0,
      revenue: Number(data.summary?.revenue ?? 0),
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadStudents(), loadClassOptions()])
})

async function loadClassOptions() {
  classOptionsLoading.value = true
  try {
    const options = await listStudentClassOptions()
    classOptions.value = options.map((item) => ({ label: item.name, value: item.id }))
  } catch (e) {
    toast.add({ severity: 'warn', summary: '班级加载失败', detail: '无法获取班级选项，可稍后重试', life: 2500 })
  } finally {
    classOptionsLoading.value = false
  }
}

function classIdFromName(className) {
  if (!className) return null
  const matched = classOptions.value.find((item) => item.label === className)
  return matched?.value || null
}

watch(statusFilter, () => {
  if (skipNextStatusReload) {
    skipNextStatusReload = false
    return
  }
  currentPage.value = 1
  first.value = 0
  loadStudents({ page: 1, pageSize: rows.value })
})

watch(search, () => {
  if (skipNextSearchReload) {
    skipNextSearchReload = false
    return
  }
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    first.value = 0
    loadStudents({ page: 1, pageSize: rows.value })
  }, 300)
})

function openCreate() { editing.value = false; form.value = { name: '', gender: '男', age: 8, status: '意向', classInfo: '', counselor: '', phone: '', remark: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row, classInfo: classIdFromName(row.classInfo) }; showEditor.value = true }

async function saveStudent() {
  try {
    const selectedClass = classOptions.value.find((item) => item.value === form.value.classInfo)
    const payload = {
      ...form.value,
      classId: form.value.classInfo || null,
      classInfo: selectedClass?.label || null,
    }
    if (editing.value) {
      await updateStudent(form.value.id, payload)
      await loadStudents()
      toast.add({ severity: 'success', summary: '更新成功', detail: `${form.value.name} 的信息已更新`, life: 3000 })
    } else {
      await createStudent({ ...payload, branchId: auth.user?.branchId })
      currentPage.value = 1
      first.value = 0
      await loadStudents({ page: 1, pageSize: rows.value })
      toast.add({ severity: 'success', summary: '新增成功', detail: `已添加学员 ${form.value.name}`, life: 3000 })
    }
    showEditor.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: '操作失败', detail: e.message, life: 3000 })
  }
}
function confirmDelete(row) {
  confirm.require({ message: `确定要删除学员「${row.name}」吗？此操作无法撤销。`, header: '删除确认', icon: 'pi pi-exclamation-triangle', acceptLabel: '删除', rejectLabel: '取消', acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await deleteStudent(row.id)
        await loadStudents()
        toast.add({ severity: 'warn', summary: '已删除', detail: `学员 ${row.name} 已被移除`, life: 3000 })
      } catch (e) {
        toast.add({ severity: 'error', summary: '删除失败', detail: e.message, life: 3000 })
      }
    }
  })
}
function applyFilters() {
  appliedFilters.value = { ...filterForm.value }
  skipNextStatusReload = true
  statusFilter.value = filterForm.value.status
  showFilter.value = false
  currentPage.value = 1
  first.value = 0
  loadStudents({ page: 1, pageSize: rows.value })
}
function resetFilters() {
  skipNextSearchReload = true
  search.value = ''
  skipNextStatusReload = true
  statusFilter.value = '全部'
  appliedFilters.value = { name: '', status: '全部', classInfo: '', counselor: '' }
  filterForm.value = { name: '', status: '全部', classInfo: '', counselor: '' }
  sortField.value = null
  sortOrder.value = null
  currentPage.value = 1
  first.value = 0
  loadStudents({ page: 1, pageSize: rows.value })
}
function handlePage(event) {
  rows.value = event.rows
  first.value = event.first
  currentPage.value = event.page + 1
  loadStudents({ page: currentPage.value, pageSize: rows.value })
}
function handleSort(event) {
  sortField.value = event.sortField
  sortOrder.value = event.sortOrder
  currentPage.value = 1
  first.value = 0
  loadStudents({ page: 1, pageSize: rows.value })
}
const showDetail = ref(false)
const activeStudent = ref(null)
function openDetail(row) { activeStudent.value = row; showDetail.value = true }
function editFromDetail() { showDetail.value = false; openEdit(activeStudent.value) }
</script>
<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.summary-card {
  background: linear-gradient(135deg, var(--color-surface) 0%, color-mix(in srgb, var(--color-surface-offset) 70%, transparent) 100%);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
}
.summary-card.accent {
  border-color: color-mix(in srgb, var(--color-primary) 24%, var(--color-divider));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--color-primary) 10%, transparent);
}
.summary-title { font-size: var(--text-xs); color: var(--color-text-faint); text-transform: uppercase; letter-spacing: 0.08em; }
.summary-value { font-size: 1.3rem; font-weight: 700; color: var(--color-text); margin-top: var(--space-1); }
.summary-meta { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: var(--space-1); }
.toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  padding: var(--space-3) var(--space-4);
  background: color-mix(in srgb, var(--color-surface) 88%, transparent);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
}
.spacer { flex: 1; }
.toolbar-actions { display: contents; }
.filter-chip-group :deep(.p-selectbutton) { display: flex; flex-wrap: wrap; gap: var(--space-2); }
.reset-filter-btn :deep(.p-button-label),
.reset-filter-btn :deep(.p-button-icon) { color: var(--color-text) !important; }
.reset-filter-btn:hover {
  background: var(--color-primary-hover) !important;
  border-color: var(--color-primary-hover) !important;
  color: #fff !important;
}
.reset-filter-btn:hover :deep(.p-button-label),
.reset-filter-btn:hover :deep(.p-button-icon) { color: #fff !important; }
.search-shell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  /* padding: 0 var(--space-3); */
  min-width: min(280px, 100%);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-full);
  background: var(--color-surface);
}
.search-icon { padding-inline-start: 22px; color: var(--color-text-faint); font-size: 0.9rem; }
.search-input {
  min-width: 0;
  border: 0;
  box-shadow: none;
  background: transparent;
}
.search-input:focus { box-shadow: none; }
.table-card {
  background: var(--color-surface);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.name-cell { display: flex; align-items: center; gap: var(--space-2); }
.name-text { font-weight: 600; color: var(--color-text); }
.name-meta { font-size: var(--text-xs); color: var(--color-text-faint); margin-top: 2px; }
.row-actions { display: flex; gap: var(--space-2); }
.icon-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  transition: all var(--transition-interactive);
}
.icon-action:hover { background: var(--color-surface-offset); color: var(--color-primary); }
.icon-action.danger:hover { color: var(--color-error); background: var(--color-error-highlight); }
.attendance-cell { display: flex; flex-direction: column; gap: 4px; min-width: 110px; }
.attendance-cell :deep(.p-progressbar) { height: 6px; border-radius: 999px; }
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-5);
  color: var(--color-text-muted);
}
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.detail-panel { display: flex; flex-direction: column; gap: var(--space-4); }
.detail-header { display: flex; align-items: center; gap: var(--space-4); }
.detail-header h3 { font-size: var(--text-lg); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); }
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--space-4); padding-top: var(--space-3); }
.detail-grid p { font-weight: 600; margin-top: var(--space-1); }
:deep(.p-datatable-tbody > tr) { cursor: pointer; }
:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: color-mix(in srgb, var(--color-surface-offset) 80%, transparent);
  color: var(--color-text-muted);
}
:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background: color-mix(in srgb, var(--color-primary-highlight) 70%, transparent);
}
:deep(.status-toggle.p-selectbutton .p-button) {
  border-radius: 20px;
  padding-inline: var(--space-3);
}
:deep(.status-toggle.p-selectbutton .p-button:not(.p-highlight)) {
  color: var(--color-text);
}
:deep(.status-toggle.p-selectbutton .p-button:not(.p-highlight) .p-button-label) {
  color: var(--color-text);
}
:deep(.status-toggle.p-selectbutton .p-button:not(.p-highlight):hover) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
  color: #fff;
}
:deep(.status-toggle.p-selectbutton .p-button:not(.p-highlight):hover .p-button-label) {
  color: #fff;
}
:deep(.status-toggle.p-selectbutton .p-button[aria-checked="true"]) {
  color: #fff;
}
:deep(.status-toggle.p-selectbutton .p-button[aria-checked="true"] .p-button-label) {
  color: #fff;
}
:deep(.status-toggle.p-selectbutton .p-button.p-highlight) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

@media (max-width: 960px) {
  .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .summary-grid { grid-template-columns: 1fr; }
  .toolbar { padding: var(--space-3); }
  .toolbar-actions { width: 100%; }
  .search-shell { width: 100%; }
}
</style>
