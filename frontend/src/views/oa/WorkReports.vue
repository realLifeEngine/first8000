<template>
  <div>
    <PageHeader title="工作报告" crumb="办公OA > 工作报告" subtitle="查看团队周报、月报与专项报告">
      <template #actions><Button label="提交报告" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="category" header="类型" sortable />
        <Column field="title" header="标题" sortable><template #body="{ data }"><span class="link-text" @click="openDetail(data)">{{ data.title }}</span></template></Column>
        <Column field="dept" header="部门" sortable /><Column field="submitter" header="提交人" sortable /><Column field="time" header="提交时间" sortable />
        <Column field="read" header="状态"><template #body="{ data }"><StatusTag :value="data.read" /></template></Column>
      </DataTable>
    </div>
    <Dialog v-model:visible="showDetail" modal header="报告详情" :style="{width:'560px'}">
      <div v-if="active" class="detail-body"><h3>{{ active.title }}</h3><p class="muted">{{ active.submitter }} · {{ active.dept }} · {{ active.time }}</p><p class="content-text">{{ active.content }}</p></div>
      <template #footer><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
    <RecordDialog v-model:visible="showEditor" title="提交工作报告" width="600px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>类型</label><Dropdown v-model="form.category" :options="['周报','月报','专项报告']" /></div>
        <div class="field"><label>部门</label><InputText v-model="form.dept" /></div>
        <div class="field full"><label>标题</label><InputText v-model="form.title" /></div>
        <div class="field full"><label>内容</label><Textarea v-model="form.content" rows="4" autoResize /></div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { workReports, nextId } from '../../data/mockData'
const toast = useToast()
const list = ref([...workReports])
const showDetail = ref(false)
const active = ref(null)
function openDetail(row) { active.value = row; showDetail.value = true }
const showEditor = ref(false)
const form = ref({ category: '周报', dept: '', title: '', content: '' })
function openCreate() { form.value = { category: '周报', dept: '', title: '', content: '' }; showEditor.value = true }
function save() { list.value.unshift({ ...form.value, id: nextId(), submitter: '管理员', time: new Date().toISOString().slice(0,10), read: '未读' }); toast.add({ severity: 'success', summary: '提交成功', life: 2500 }); showEditor.value = false }
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.link-text { cursor: pointer; }
.link-text:hover { color: var(--color-primary); }
.detail-body h3 { font-size: var(--text-lg); margin-bottom: var(--space-2); }
.muted { color: var(--color-text-muted); font-size: var(--text-xs); margin-bottom: var(--space-3); }
.content-text { font-size: var(--text-sm); line-height: 1.7; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
