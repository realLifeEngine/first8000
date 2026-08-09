<template>
  <div>
    <PageHeader title="请假条" crumb="办公OA > 请假条" subtitle="外出与请假申请审批记录">
      <template #actions><Button v-if="auth.can('leave:create')" label="新建申请" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="applyDate" header="申请日期" sortable /><Column field="applicant" header="申请人" sortable /><Column field="type" header="类型" sortable /><Column field="reason" header="事由" />
        <Column field="outTime" header="外出时间" /><Column field="backTime" header="返回时间" /><Column field="absenceDays" header="缺勤天数" sortable />
        <Column field="audit" header="审批状态" sortable><template #body="{ data }"><StatusTag :value="data.audit" /></template></Column>
        <Column header="管理" style="width:90px"><template #body="{ data }"><Button v-if="data.audit==='审批中' && auth.can('leave:approve')" label="批准" size="small" text @click="approve(data)" /></template></Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" title="新建请假/外出申请" width="600px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>类型</label><Dropdown v-model="form.type" :options="['家访','外出培训','请假']" /></div>
        <div class="field"><label>缺勤天数</label><InputNumber v-model="form.absenceDays" :min="0.5" :step="0.5" mode="decimal" /></div>
        <div class="field"><label>外出时间</label><InputText v-model="form.outTime" placeholder="如：09:00" /></div>
        <div class="field"><label>返回时间</label><InputText v-model="form.backTime" placeholder="如：13:00" /></div>
        <div class="field full"><label>事由</label><Textarea v-model="form.reason" rows="3" autoResize /></div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { leaveRequests } from '../../api/oa'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])
const loading = ref(false)
const showEditor = ref(false)
const form = ref({ type: '请假', absenceDays: 0.5, outTime: '', backTime: '', reason: '' })

async function loadLeaveRequests() {
  loading.value = true
  try {
    const data = await leaveRequests.list()
    list.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadLeaveRequests())

function openCreate() { form.value = { type: '请假', absenceDays: 0.5, outTime: '', backTime: '', reason: '' }; showEditor.value = true }

async function save() {
  try {
    await leaveRequests.create(form.value)
    await loadLeaveRequests()
    toast.add({ severity: 'success', summary: '申请已提交', life: 2500 })
    showEditor.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: '申请失败', detail: e.message, life: 3000 })
  }
}

async function approve(row) {
  try {
    await leaveRequests.approve(row.id, {})
    await loadLeaveRequests()
    toast.add({ severity: 'success', summary: '已批准', detail: `${row.applicant} 的申请已批准`, life: 2500 })
  } catch (e) {
    toast.add({ severity: 'error', summary: '操作失败', detail: e.message, life: 3000 })
  }
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
