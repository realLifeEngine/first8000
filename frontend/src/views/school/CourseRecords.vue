<template>
  <div>
    <PageHeader title="教课记录" crumb="教务管理 > 教课记录" subtitle="查看和管理教师授课明细记录">
      <template #actions><Button label="登记教课" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <TabView v-model:activeIndex="tabIndex">
      <TabPanel header="全部记录">
        <div class="table-card">
          <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
            <Column field="date" header="日期" sortable /><Column field="teacher" header="教师" sortable /><Column field="student" header="学员" sortable /><Column field="course" header="课程" /><Column field="topic" header="主题" /><Column field="duration" header="时长(分钟)" sortable />
            <Column field="status" header="点评状态" sortable><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
            <Column header="管理" style="width:90px"><template #body="{ data }"><button class="icon-action" @click="openEdit(data)"><Pencil :size="15" /></button></template></Column>
          </DataTable>
        </div>
      </TabPanel>
      <TabPanel header="待评列表">
        <div class="table-card">
          <DataTable :value="list.filter(r => r.status === '待评')" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows>
            <Column field="date" header="日期" /><Column field="teacher" header="教师" /><Column field="student" header="学员" /><Column field="course" header="课程" />
            <Column header="操作" style="width:100px"><template #body="{ data }"><Button label="去点评" size="small" text @click="openEdit(data)" /></template></Column>
          </DataTable>
        </div>
      </TabPanel>
    </TabView>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑教课记录' : '登记教课记录'" width="600px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>教师</label><Dropdown v-model="form.teacher" :options="teacherNames" /></div>
        <div class="field"><label>学员</label><InputText v-model="form.student" /></div>
        <div class="field"><label>课程</label><InputText v-model="form.course" /></div>
        <div class="field"><label>主题</label><InputText v-model="form.topic" /></div>
        <div class="field"><label>日期</label><InputText v-model="form.date" placeholder="YYYY-MM-DD" /></div>
        <div class="field"><label>时长(分钟)</label><InputNumber v-model="form.duration" /></div>
        <div class="field full"><label>课堂评价</label><Textarea v-model="form.comment" rows="3" autoResize placeholder="填写课堂表现点评..." /></div>
        <div class="field full"><label>星级评分</label><Rating v-model="form.rating" :cancel="false" /></div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Pencil } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Rating from 'primevue/rating'
import { useToast } from 'primevue/usetoast'
import { courseRecords, teachers, nextId } from '../../data/mockData'
const toast = useToast()
const list = ref([...courseRecords])
const tabIndex = ref(0)
const teacherNames = teachers.map(t => t.nickname)
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ teacher: teacherNames[0], student: '', course: '', topic: '', date: '', duration: 60, comment: '', rating: 0 })
function openCreate() { editing.value = false; form.value = { teacher: teacherNames[0], student: '', course: '', topic: '', date: '', duration: 60, comment: '', rating: 0, status: '待评' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row }; showEditor.value = true }
function save() {
  if (editing.value) { const idx = list.value.findIndex(r => r.id === form.value.id); if (idx > -1) list.value[idx] = { ...list.value[idx], ...form.value, status: form.value.comment ? '已评' : '待评' }; toast.add({ severity: 'success', summary: '更新成功', life: 2500 }) }
  else { list.value.unshift({ ...form.value, id: nextId(), time: '14:00', status: form.value.comment ? '已评' : '待评' }); toast.add({ severity: 'success', summary: '登记成功', life: 2500 }) }
  showEditor.value = false
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.icon-action { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: var(--radius-md); color: var(--color-text-muted); }
.icon-action:hover { background: var(--color-surface-offset); color: var(--color-primary); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
