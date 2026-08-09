<template>
  <div>
    <PageHeader title="校区管理" crumb="系统管理 > 校区管理" subtitle="多校区档案与基础信息维护">
      <template #actions><Button label="新增校区" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>

    <div class="summary-card">
      <div>
        <div class="summary-title">校区总览</div>
        <div class="summary-value">{{ list.length }} 个校区</div>
      </div>
      <Button label="新增校区" icon="pi pi-plus" @click="openCreate" />
    </div>

    <div class="table-card">
      <DataTable :value="list" :loading="loading" paginator :rows="8" :rowsPerPageOptions="[8, 12]" dataKey="id" responsiveLayout="scroll" stripedRows showGridlines rowHover>
        <template #empty>
          <div class="empty-state"><i class="pi pi-map-marker" /><span>当前暂无校区信息。</span></div>
        </template>
        <Column field="name" header="校区名称" sortable />
        <Column field="address" header="地址" />
        <Column field="phone" header="联系电话" />
        <Column header="操作" style="width:140px">
          <template #body="{ data }">
            <div class="row-actions">
              <button class="icon-action" type="button" aria-label="编辑校区" @click="openEdit(data)"><i class="pi pi-pencil" /></button>
              <button class="icon-action danger" type="button" aria-label="删除校区" @click="remove(data)"><i class="pi pi-trash" /></button>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑校区' : '新增校区'" width="520px" @confirm="save">
      <div class="form-grid">
        <div class="field full">
          <label>校区名称</label>
          <InputText v-model="form.name" :invalid="!!formErrors.name" @input="clearFieldError('name')" />
          <small v-if="formErrors.name" class="field-error">{{ formErrors.name }}</small>
        </div>
        <div class="field full">
          <label>校区编码</label>
          <InputText v-model="form.code" :disabled="editing" :invalid="!!formErrors.code" @input="clearFieldError('code')" placeholder="例如: XJ-TS-RD" />
          <small v-if="formErrors.code" class="field-error">{{ formErrors.code }}</small>
        </div>
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
const form = ref({ name: '', code: '', address: '', phone: '' })
const formErrors = ref({ name: '', code: '' })

function resetFormErrors() {
  formErrors.value = { name: '', code: '' }
}

function clearFieldError(field) {
  formErrors.value[field] = ''
}

function validateForm() {
  resetFormErrors()
  const name = String(form.value.name || '').trim()
  const code = String(form.value.code || '').trim()
  if (!name) formErrors.value.name = '请输入校区名称'
  if (!editing.value && !code) formErrors.value.code = '请输入校区编码'
  return !Object.values(formErrors.value).some(Boolean)
}

function openCreate() {
  editing.value = false
  resetFormErrors()
  form.value = { name: '', code: '', address: '', phone: '' }
  showEditor.value = true
}

function openEdit(row) {
  editing.value = true
  resetFormErrors()
  form.value = { ...row }
  showEditor.value = true
}

async function save() {
  try {
    if (!validateForm()) {
      toast.add({ severity: 'warn', summary: '请先修正表单错误', life: 2500 })
      return
    }

    const name = String(form.value.name || '').trim()
    const code = String(form.value.code || '').trim()
    const address = String(form.value.address || '').trim()
    const phone = String(form.value.phone || '').trim()

    if (editing.value) {
      const updated = await updateBranch(form.value.id, {
        name,
        address: address || null,
        phone: phone || null,
      })
      const idx = list.value.findIndex(b => b.id === form.value.id)
      if (idx > -1) list.value[idx] = updated
      toast.add({ severity: 'success', summary: '更新成功', life: 2500 })
    } else {
      const created = await createBranch({
        name,
        code,
        address: address || null,
        phone: phone || null,
      })
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
.summary-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background: linear-gradient(135deg, var(--color-surface) 0%, color-mix(in srgb, var(--color-surface-offset) 70%, transparent) 100%);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-lg);
}
.summary-title { font-size: var(--text-xs); color: var(--color-text-faint); text-transform: uppercase; letter-spacing: 0.08em; }
.summary-value { margin-top: var(--space-1); font-size: 1.1rem; font-weight: 700; color: var(--color-text); }
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-xl); overflow: hidden; box-shadow: var(--shadow-sm); }
.row-actions { display: flex; gap: var(--space-2); }
.icon-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  transition: color var(--transition-interactive), background-color var(--transition-interactive);
}
.icon-action:hover {
  background: var(--color-surface-offset);
  color: var(--color-primary);
}
.icon-action.danger:hover {
  background: var(--color-error-highlight);
  color: var(--color-error);
}
.empty-state { display: flex; align-items: center; justify-content: center; gap: var(--space-2); padding: var(--space-5); color: var(--color-text-muted); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field.full { grid-column: 1 / -1; }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.field-error { color: var(--color-error); font-size: var(--text-xs); line-height: 1.2; }
</style>
