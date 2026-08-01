<template>
  <div>
    <PageHeader title="资产管理" crumb="办公OA > 资产管理" subtitle="教学与办公设备台账管理">
      <template #actions><Button label="登记资产" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="name" header="资产名称" sortable /><Column field="type" header="类别" sortable /><Column field="recordDate" header="登记日期" sortable />
        <Column field="value" header="原值" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.value).toLocaleString() }}</span></template></Column>
        <Column field="currentValue" header="当前净值"><template #body="{ data }"><span class="tabular">¥{{ Number(data.currentValue).toLocaleString() }}</span></template></Column>
        <Column field="keeper" header="保管人" sortable /><Column field="status" header="状态" sortable><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
        <Column header="管理" style="width:90px"><template #body="{ data }"><button class="icon-action" @click="openEdit(data)"><Pencil :size="15" /></button></template></Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" :title="editing?'编辑资产':'登记资产'" width="600px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>资产名称</label><InputText v-model="form.name" /></div>
        <div class="field"><label>类别</label><Dropdown v-model="form.type" :options="['教学设备','办公设备','乐器']" /></div>
        <div class="field"><label>原值</label><InputNumber v-model="form.valueNum" mode="currency" currency="CNY" locale="zh-CN" /></div>
        <div class="field"><label>保管人</label><InputText v-model="form.keeper" /></div>
        <div class="field"><label>状态</label><Dropdown v-model="form.status" :options="['正常','已报废']" /></div>
        <div class="field full"><label>说明</label><Textarea v-model="form.desc" rows="3" autoResize /></div>
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
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import { useToast } from 'primevue/usetoast'
import { properties, nextId } from '../../data/mockData'
const toast = useToast()
const list = ref([...properties])
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ name: '', type: '教学设备', valueNum: 0, keeper: '', status: '正常', desc: '' })
function openCreate() { editing.value = false; form.value = { name: '', type: '教学设备', valueNum: 0, keeper: '', status: '正常', desc: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row, valueNum: Number(row.value) }; showEditor.value = true }
function save() {
  const payload = { ...form.value, value: String(form.value.valueNum), currentValue: String(Math.round(form.value.valueNum * 0.85)) }
  if (editing.value) { const idx = list.value.findIndex(p => p.id === payload.id); if (idx > -1) list.value[idx] = { ...list.value[idx], ...payload }; toast.add({ severity: 'success', summary: '更新成功', life: 2500 }) }
  else { list.value.unshift({ ...payload, id: nextId(), recordDate: new Date().toISOString().slice(0,10), depreciationRate: '10%', dept: '行政部', scrapped: '否', entryTime: new Date().toISOString().slice(0,10) }); toast.add({ severity: 'success', summary: '登记成功', life: 2500 }) }
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
