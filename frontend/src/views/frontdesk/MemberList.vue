<template>
  <div>
    <PageHeader title="会员管理" crumb="前台业务 > 会员管理" subtitle="学员全生命周期信息与业务指标">
      <template #actions>
        <Button label="高级搜索" icon="pi pi-filter" outlined @click="showFilter = true" />
        <Button label="新增学员" icon="pi pi-plus" @click="openCreate" />
      </template>
    </PageHeader>
    <div class="toolbar">
      <SelectButton v-model="statusFilter" :options="['全部', ...statuses]" />
      <span class="spacer"></span>
      <InputText v-model="search" placeholder="搜索学员姓名..." class="search-input" />
    </div>
    <div class="table-card">
      <DataTable :value="filtered" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows @row-click="openDetail($event.data)" removableSort>
        <Column field="name" header="学员姓名" sortable>
          <template #body="{ data }"><div class="name-cell"><Avatar :label="data.name.charAt(0)" shape="circle" size="normal" /><span>{{ data.name }}</span></div></template>
        </Column>
        <Column field="gender" header="性别" sortable />
        <Column field="age" header="年龄" sortable />
        <Column field="status" header="业务状态" sortable><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
        <Column field="classInfo" header="班级信息" sortable />
        <Column field="totalPaid" header="总收款" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.totalPaid).toLocaleString() }}</span></template></Column>
        <Column field="consumed" header="消课" sortable />
        <Column field="onTimeRate" header="准时出勤" sortable />
        <Column field="counselor" header="学管老师" sortable />
        <Column header="管理" style="width:110px">
          <template #body="{ data }">
            <div class="row-actions" @click.stop>
              <button class="icon-action" @click="openEdit(data)" aria-label="编辑"><Pencil :size="15" /></button>
              <button class="icon-action danger" @click="confirmDelete(data)" aria-label="删除"><Trash2 :size="15" /></button>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showFilter" title="按条件筛选" width="640px" confirm-label="筛选" @confirm="showFilter=false">
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
        <div class="field"><label>班级信息</label><InputText v-model="form.classInfo" /></div>
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
import { ref, computed } from 'vue'
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
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { students as seedStudents, businessStatuses, nextId } from '../../data/mockData'
const toast = useToast()
const confirm = useConfirm()
const statuses = businessStatuses
const list = ref([...seedStudents])
const search = ref('')
const statusFilter = ref('全部')
const filtered = computed(() => list.value.filter(s => (statusFilter.value === '全部' || s.status === statusFilter.value) && (!search.value || s.name.includes(search.value))))
const showFilter = ref(false)
const filterForm = ref({ name: '', status: '全部', classInfo: '', counselor: '' })
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ name: '', gender: '男', age: 8, status: '意向', classInfo: '', counselor: '', phone: '', remark: '' })
function openCreate() { editing.value = false; form.value = { name: '', gender: '男', age: 8, status: '意向', classInfo: '', counselor: '', phone: '', remark: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row }; showEditor.value = true }
function saveStudent() {
  if (editing.value) {
    const idx = list.value.findIndex(s => s.id === form.value.id)
    if (idx > -1) list.value[idx] = { ...list.value[idx], ...form.value }
    toast.add({ severity: 'success', summary: '更新成功', detail: `${form.value.name} 的信息已更新`, life: 3000 })
  } else {
    list.value.unshift({ ...form.value, id: nextId(), totalPaid: '0', consumed: 0, absence: 0, onTimeRate: '0%', lastConsume: '-', consumeFreq: '-', reviewViews: 0, viewRate: '0%', lastContact: '-', nextContact: '-', regular: 0, gift: 0, other: 0, stored: '0' })
    toast.add({ severity: 'success', summary: '新增成功', detail: `已添加学员 ${form.value.name}`, life: 3000 })
  }
  showEditor.value = false
}
function confirmDelete(row) {
  confirm.require({ message: `确定要删除学员「${row.name}」吗？此操作无法撤销。`, header: '删除确认', icon: 'pi pi-exclamation-triangle', acceptLabel: '删除', rejectLabel: '取消', acceptClass: 'p-button-danger',
    accept: () => { list.value = list.value.filter(s => s.id !== row.id); toast.add({ severity: 'warn', summary: '已删除', detail: `学员 ${row.name} 已被移除`, life: 3000 }) } })
}
const showDetail = ref(false)
const activeStudent = ref(null)
function openDetail(row) { activeStudent.value = row; showDetail.value = true }
function editFromDetail() { showDetail.value = false; openEdit(activeStudent.value) }
</script>
<style scoped>
.toolbar { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); flex-wrap: wrap; }
.spacer { flex: 1; }
.search-input { min-width: 220px; }
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.name-cell { display: flex; align-items: center; gap: var(--space-2); }
.row-actions { display: flex; gap: var(--space-2); }
.icon-action { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: var(--radius-md); color: var(--color-text-muted); }
.icon-action:hover { background: var(--color-surface-offset); color: var(--color-primary); }
.icon-action.danger:hover { color: var(--color-error); background: var(--color-error-highlight); }
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
</style>
