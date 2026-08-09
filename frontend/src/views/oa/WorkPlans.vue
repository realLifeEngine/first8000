<template>
  <div>
    <PageHeader title="工作计划" crumb="办公OA > 工作计划" subtitle="跟踪团队工作计划的进度与反馈">
      <template #actions><Button v-if="auth.can('plan:create')" label="新建计划" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="title" header="标题" sortable><template #body="{ data }"><span class="link-text" @click="openDetail(data)">{{ data.title }}</span></template></Column>
        <Column field="owner" header="负责人" sortable /><Column field="priority" header="优先级" sortable><template #body="{ data }"><StatusTag :value="data.priority" /></template></Column>
        <!-- <Column field="progress" header="进度"><template #body="{ data }"><ProgressBar :value="Number(data.progress)" style="height:8px" /></template></Column> -->
        <Column field="deadline" header="截止时间" sortable /><Column field="read" header="状态"><template #body="{ data }"><StatusTag :value="data.read" /></template></Column>
        <Column header="管理" style="width:90px"><template #body="{ data }"><button v-if="auth.can('plan:edit')" class="icon-action" @click="openEdit(data)"><Pencil :size="15" /></button></template></Column>
      </DataTable>
    </div>
    <Dialog v-model:visible="showDetail" modal header="工作计划详情" :style="{width:'520px'}">
      <div v-if="active" class="detail-view">
        <div class="detail-row"><span>标题</span><strong>{{ active.title }}</strong></div>
        <div class="detail-row"><span>负责人</span><span>{{ active.owner }}</span></div>
        <div class="detail-row"><span>发起人</span><span>{{ active.initiator }}</span></div>
        <div class="detail-row"><span>参与人数</span><span>{{ active.participants }}</span></div>
        <div class="detail-row"><span>截止时间</span><span>{{ active.deadline }}</span></div>
        <div class="detail-row"><span>进度</span><ProgressBar :value="Number(active.progress)" /></div>
        <div class="detail-row"><span>反馈</span><span>{{ active.feedback }}</span></div>
      </div>
      <template #footer><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
    <RecordDialog v-model:visible="showEditor" :title="editing?'编辑计划':'新建工作计划'" width="600px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>标题</label><InputText v-model="form.title" /></div>
        <div class="field"><label>负责人</label><InputText v-model="form.owner" /></div>
        <div class="field"><label>优先级</label><Dropdown v-model="form.priority" :options="['高','中','低']" /></div>
        <div class="field"><label>截止时间</label><InputText v-model="form.deadline" placeholder="YYYY-MM-DD" /></div>
        <div class="field full"><label>进度(%)</label><Slider v-model="form.progressNum" /><span class="tabular">{{ form.progressNum }}%</span></div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref, watch, onMounted } from 'vue'
import { Pencil } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import ProgressBar from 'primevue/progressbar'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Slider from 'primevue/slider'
import { useToast } from 'primevue/usetoast'
import { workPlans } from '../../api/oa'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])
const loading = ref(false)
const showDetail = ref(false)
const active = ref(null)
function openDetail(row) { active.value = row; showDetail.value = true }
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ title: '', owner: '', priority: '中', deadline: '', progressNum: 0 })
watch(() => form.value.progressNum, v => form.value.progress = String(v))

async function loadWorkPlans() {
  loading.value = true
  try {
    const data = await workPlans.list()
    list.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadWorkPlans())

function openCreate() { editing.value = false; form.value = { title: '', owner: '', priority: '中', deadline: '', progressNum: 0, progress: '0' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row, progressNum: Number(row.progress) }; showEditor.value = true }

async function save() {
  try {
    const payload = { ...form.value, progress: String(form.value.progressNum) }
    if (editing.value) {
      await workPlans.update(payload.id, payload)
      await loadWorkPlans()
      toast.add({ severity: 'success', summary: '更新成功', life: 2500 })
    } else {
      await workPlans.create(payload)
      await loadWorkPlans()
      toast.add({ severity: 'success', summary: '新建成功', life: 2500 })
    }
    showEditor.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: '操作失败', detail: e.message, life: 3000 })
  }
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.link-text { cursor: pointer; }
.link-text:hover { color: var(--color-primary); }
.icon-action { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: var(--radius-md); color: var(--color-text-muted); }
.icon-action:hover { background: var(--color-surface-offset); color: var(--color-primary); }
.detail-view { display: flex; flex-direction: column; gap: var(--space-3); }
.detail-row { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); font-size: var(--text-sm); }
.detail-row span:first-child { color: var(--color-text-muted); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
