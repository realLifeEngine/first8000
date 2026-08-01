<template>
  <div>
    <PageHeader title="内部公文" crumb="办公OA > 内部公文" subtitle="发布与查阅机构行政通知">
      <template #actions><Button label="发布公文" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="category" header="分类" sortable />
        <Column header="标题" sortable field="title"><template #body="{ data }"><div class="title-cell"><Star v-if="data.starred" :size="14" class="star" /><span @click="openDetail(data)" class="link-text">{{ data.title }}</span></div></template></Column>
        <Column field="publisher" header="发布人" sortable /><Column field="createTime" header="发布时间" sortable />
        <Column field="status" header="状态" sortable><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
        <Column header="管理" style="width:90px"><template #body="{ data }"><button class="icon-action" @click="openEdit(data)"><Pencil :size="15" /></button></template></Column>
      </DataTable>
    </div>
    <Dialog v-model:visible="showDetail" modal header="公文详情" :style="{width:'560px'}">
      <div v-if="active" class="detail-body"><h3>{{ active.title }}</h3><p class="muted">{{ active.publisher }} · {{ active.createTime }}</p><p class="content-text">{{ active.content }}</p></div>
      <template #footer><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
    <RecordDialog v-model:visible="showEditor" :title="editing?'编辑公文':'发布公文'" width="620px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>分类</label><Dropdown v-model="form.category" :options="['行政通知','教务通知','人事通知','系统公告']" /></div>
        <div class="field"><label>状态</label><Dropdown v-model="form.status" :options="['正常','进行中','已完成']" /></div>
        <div class="field full"><label>标题</label><InputText v-model="form.title" /></div>
        <div class="field full"><label>内容</label><Textarea v-model="form.content" rows="4" autoResize /></div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Star, Pencil } from 'lucide-vue-next'
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
import { notices, nextId } from '../../data/mockData'
const toast = useToast()
const list = ref([...notices])
const showDetail = ref(false)
const active = ref(null)
function openDetail(row) { active.value = row; showDetail.value = true }
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ category: '行政通知', status: '正常', title: '', content: '' })
function openCreate() { editing.value = false; form.value = { category: '行政通知', status: '正常', title: '', content: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row }; showEditor.value = true }
function save() {
  if (editing.value) { const idx = list.value.findIndex(n => n.id === form.value.id); if (idx > -1) list.value[idx] = { ...list.value[idx], ...form.value }; toast.add({ severity: 'success', summary: '更新成功', life: 2500 }) }
  else { list.value.unshift({ ...form.value, id: nextId(), publisher: '管理员', createTime: new Date().toISOString().slice(0,10), starred: false, pinned: false }); toast.add({ severity: 'success', summary: '发布成功', life: 2500 }) }
  showEditor.value = false
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.title-cell { display: flex; align-items: center; gap: var(--space-2); }
.star { color: var(--color-warning); flex-shrink: 0; }
.link-text { cursor: pointer; }
.link-text:hover { color: var(--color-primary); }
.icon-action { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: var(--radius-md); color: var(--color-text-muted); }
.icon-action:hover { background: var(--color-surface-offset); color: var(--color-primary); }
.detail-body h3 { font-size: var(--text-lg); margin-bottom: var(--space-2); }
.muted { color: var(--color-text-muted); font-size: var(--text-xs); margin-bottom: var(--space-3); }
.content-text { font-size: var(--text-sm); line-height: 1.7; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
