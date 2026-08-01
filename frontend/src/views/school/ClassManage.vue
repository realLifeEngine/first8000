<template>
  <div>
    <PageHeader title="班级管理" crumb="教务管理 > 班级管理" subtitle="维护班级排课、容量与主题信息">
      <template #actions><Button label="新增班级" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="type" header="班级类型" sortable /><Column field="date" header="日期" /><Column field="time" header="时段" /><Column field="course" header="默认课程" sortable /><Column field="remark" header="名称备注" /><Column field="weekTopic" header="本周主题" />
        <Column field="capacity" header="班容情况" sortable><template #body="{ data }"><div class="capacity-cell"><ProgressBar :value="capacityPct(data.capacity)" :showValue="false" style="width:80px;height:8px" /><span class="tabular">{{ data.capacity }}</span></div></template></Column>
        <Column field="campus" header="隶属校区" sortable /><Column field="weekStatus" header="本周" sortable><template #body="{ data }"><StatusTag :value="data.weekStatus" /></template></Column>
        <Column header="管理" style="width:110px"><template #body="{ data }"><div class="row-actions"><button class="icon-action" @click="openEdit(data)"><Pencil :size="15" /></button><button class="icon-action" @click="viewStudents(data)"><Users :size="15" /></button></div></template></Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑班级' : '新增班级'" width="640px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>班级类型</label><Dropdown v-model="form.type" :options="['常规班','精品班','集训班','短期班']" /></div>
        <div class="field"><label>隶属校区</label><InputText v-model="form.campus" /></div>
        <div class="field"><label>上课日期</label><InputText v-model="form.date" placeholder="如：周一/周三/周五" /></div>
        <div class="field"><label>上课时段</label><InputText v-model="form.time" placeholder="如：16:00-17:30" /></div>
        <div class="field"><label>默认课程</label><InputText v-model="form.course" /></div>
        <div class="field"><label>班容 (已报/上限)</label><InputText v-model="form.capacity" placeholder="如：12/15" /></div>
        <div class="field full"><label>名称备注</label><InputText v-model="form.remark" /></div>
        <div class="field full"><label>本周主题</label><InputText v-model="form.weekTopic" /></div>
      </div>
    </RecordDialog>
    <Dialog v-model:visible="showStudents" modal header="班级学员列表" :style="{ width: '520px' }">
      <p class="muted" v-if="activeClass">{{ activeClass.remark }} · {{ activeClass.studentInfo }}</p>
      <ul class="student-mini-list" role="list"><li v-for="s in mockClassStudents" :key="s.id"><Avatar :label="s.name.charAt(0)" shape="circle" size="normal" /><span>{{ s.name }}</span><StatusTag :value="s.status" /></li></ul>
      <template #footer><Button label="关闭" @click="showStudents = false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Pencil, Users } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import ProgressBar from 'primevue/progressbar'
import Dialog from 'primevue/dialog'
import Avatar from 'primevue/avatar'
import { useToast } from 'primevue/usetoast'
import { classes, students, nextId } from '../../data/mockData'
const toast = useToast()
const list = ref([...classes])
function capacityPct(cap) { const [a, b] = cap.split('/').map(Number); return Math.round((a / b) * 100) }
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ type: '常规班', campus: '总校区', date: '', time: '', course: '', capacity: '', remark: '', weekTopic: '' })
function openCreate() { editing.value = false; form.value = { type: '常规班', campus: '总校区', date: '', time: '', course: '', capacity: '', remark: '', weekTopic: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row }; showEditor.value = true }
function save() {
  if (editing.value) { const idx = list.value.findIndex(c => c.id === form.value.id); if (idx > -1) list.value[idx] = { ...list.value[idx], ...form.value }; toast.add({ severity: 'success', summary: '更新成功', life: 2500 }) }
  else { list.value.unshift({ ...form.value, id: nextId(), weekStatus: '进行中', studentInfo: '0人' }); toast.add({ severity: 'success', summary: '新增成功', life: 2500 }) }
  showEditor.value = false
}
const showStudents = ref(false)
const activeClass = ref(null)
const mockClassStudents = ref([])
function viewStudents(row) { activeClass.value = row; mockClassStudents.value = students.slice(0, 6); showStudents.value = true }
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.capacity-cell { display: flex; align-items: center; gap: var(--space-2); }
.row-actions { display: flex; gap: var(--space-2); }
.icon-action { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: var(--radius-md); color: var(--color-text-muted); }
.icon-action:hover { background: var(--color-surface-offset); color: var(--color-primary); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); margin-bottom: var(--space-3); }
.student-mini-list { display: flex; flex-direction: column; gap: var(--space-2); }
.student-mini-list li { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2); border-radius: var(--radius-md); }
.student-mini-list li:hover { background: var(--color-surface-offset); }
.student-mini-list li span { flex: 1; }
</style>
