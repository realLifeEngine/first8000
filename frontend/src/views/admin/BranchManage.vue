<template>
  <div>
    <PageHeader title="校区管理" crumb="系统管理 > 校区管理" subtitle="多校区档案与基础信息维护">
      <template #actions><Button label="新增校区" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" :loading="loading" dataKey="id" responsiveLayout="scroll" stripedRows>
        <Column field="name" header="校区名称" sortable />
        <Column field="address" header="地址" />
        <Column field="phone" header="联系电话" />
        <Column header="操作" style="width:140px">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" text size="small" @click="openEdit(data)" />
            <Button icon="pi pi-trash" text size="small" severity="danger" @click="remove(data)" />
          </template>
        </Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑校区' : '新增校区'" width="520px" @confirm="save">
      <div class="form-grid">
        <div class="field full"><label>校区名称</label><InputText v-model="form.name" /></div>
        <div class="field full"><label>地址</label><InputText v-model="form.address" /></div>
        <div class="field full"><label>联系电话</label><InputText v-model="form.phone" /></div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { listBranches, createBranch, updateBranch, deleteBranch } from '../../api/branches'

const toast = useToast()
const confirm = useConfirm()
const list = ref([])
const loading = ref(false)

async function fetchBranches() {
  loading.value = true
  try {
    const res = await listBranches({ page: 1, page_size: 100 })
    list.value = res.items
  } catch (err) {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取校区列表', life: 3000 })
  } finally {
    loading.value = false
  }
}
fetchBranches()

const showEditor = ref(false)
const editing = ref(false)
const form = ref({ name: '', address: '', phone: '' })
function openCreate() { editing.value = false; form.value = { name: '', address: '', phone: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row }; showEditor.value = true }

async function save() {
  try {
    if (editing.value) {
      const updated = await updateBranch(form.value.id, form.value)
      const idx = list.value.findIndex(b => b.id === form.value.id)
      if (idx > -1) list.value[idx] = updated
      toast.add({ severity: 'success', summary: '更新成功', life: 2500 })
    } else {
      const created = await createBranch(form.value)
      list.value.unshift(created)
      toast.add({ severity: 'success', summary: '新增成功', life: 2500 })
    }
    showEditor.value = false
  } catch (err) {
    toast.add({ severity: 'error', summary: '操作失败', detail: err.response?.data?.detail || '请稍后重试', life: 3000 })
  }
}

function remove(row) {
  confirm.require({
    message: `确定要删除校区「${row.name}」吗？`, header: '删除确认', icon: 'pi pi-exclamation-triangle',
    acceptLabel: '删除', rejectLabel: '取消', acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await deleteBranch(row.id)
        list.value = list.value.filter(b => b.id !== row.id)
        toast.add({ severity: 'warn', summary: '已删除', life: 2500 })
      } catch (err) {
        toast.add({ severity: 'error', summary: '删除失败', detail: err.response?.data?.detail || '请稍后重试', life: 3000 })
      }
    },
  })
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
</style>
