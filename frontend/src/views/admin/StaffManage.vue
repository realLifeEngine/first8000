<template>
  <div>
    <PageHeader title="员工管理" crumb="系统管理 > 员工管理" subtitle="员工账号、角色与权限管理">
      <template #actions><Button label="新增员工" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" :loading="loading" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows>
        <Column field="name" header="姓名" sortable />
        <Column field="username" header="用户名" sortable />
        <Column field="role" header="角色" sortable />
        <Column field="dept" header="部门" />
        <Column field="is_active" header="状态"><template #body="{ data }">{{ data.is_active ? '启用' : '禁用' }}</template></Column>
        <Column header="操作" style="width:160px">
          <template #body="{ data }">
            <Button icon="pi pi-key" text size="small" @click="openPermissions(data)" />
            <Button icon="pi pi-pencil" text size="small" @click="openEdit(data)" />
            <Button icon="pi pi-trash" text size="small" severity="danger" @click="remove(data)" />
          </template>
        </Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑员工' : '新增员工'" width="560px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>姓名</label><InputText v-model="form.name" /></div>
        <div class="field"><label>用户名</label><InputText v-model="form.username" :disabled="editing" /></div>
        <div v-if="!editing" class="field"><label>初始密码</label><Password v-model="form.password" :feedback="false" toggleMask /></div>
        <div class="field"><label>角色</label><Dropdown v-model="form.role" :options="['teacher','manager','school_admin','superuser']" /></div>
        <div class="field"><label>部门</label><InputText v-model="form.dept" /></div>
      </div>
    </RecordDialog>
    <Dialog v-model:visible="showPerms" modal header="权限管理" :style="{ width: '480px' }">
      <div v-if="permTarget" class="perm-list">
        <p class="muted">{{ permTarget.name }} 的有效权限：</p>
        <div class="perm-tags"><span v-for="p in currentPermissions" :key="p" class="perm-tag">{{ p }}</span></div>
        <div class="field">
          <label>授予/撤销权限</label>
          <div class="perm-grant-row">
            <InputText v-model="grantKey" placeholder="permission:key" style="flex:1" />
            <Button label="授予" size="small" @click="grant(true)" />
            <Button label="撤销" size="small" severity="danger" @click="grant(false)" />
          </div>
        </div>
      </div>
      <template #footer><Button label="关闭" @click="showPerms = false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Dropdown from 'primevue/dropdown'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { listStaff, createStaff, updateStaff, deleteStaff, getStaffPermissions, setStaffPermission } from '../../api/staff'

const toast = useToast()
const confirm = useConfirm()
const list = ref([])
const loading = ref(false)

async function fetchStaff() {
  loading.value = true
  try {
    const res = await listStaff({ page: 1, page_size: 100 })
    list.value = res.items
  } catch (err) {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取员工列表', life: 3000 })
  } finally {
    loading.value = false
  }
}
fetchStaff()

const showEditor = ref(false)
const editing = ref(false)
const form = ref({ name: '', username: '', password: '', role: 'teacher', dept: '' })
function openCreate() { editing.value = false; form.value = { name: '', username: '', password: '', role: 'teacher', dept: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row }; showEditor.value = true }

async function save() {
  try {
    if (editing.value) {
      const updated = await updateStaff(form.value.id, form.value)
      const idx = list.value.findIndex(s => s.id === form.value.id)
      if (idx > -1) list.value[idx] = updated
      toast.add({ severity: 'success', summary: '更新成功', life: 2500 })
    } else {
      const created = await createStaff(form.value)
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
    message: `确定要删除员工「${row.name}」吗？`, header: '删除确认', icon: 'pi pi-exclamation-triangle',
    acceptLabel: '删除', rejectLabel: '取消', acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await deleteStaff(row.id)
        list.value = list.value.filter(s => s.id !== row.id)
        toast.add({ severity: 'warn', summary: '已删除', life: 2500 })
      } catch (err) {
        toast.add({ severity: 'error', summary: '删除失败', detail: err.response?.data?.detail || '请稍后重试', life: 3000 })
      }
    },
  })
}

const showPerms = ref(false)
const permTarget = ref(null)
const currentPermissions = ref([])
const grantKey = ref('')

async function openPermissions(row) {
  permTarget.value = row
  grantKey.value = ''
  try {
    currentPermissions.value = await getStaffPermissions(row.id)
    showPerms.value = true
  } catch (err) {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取权限列表', life: 3000 })
  }
}

async function grant(isGranted) {
  if (!grantKey.value) return
  try {
    await setStaffPermission(permTarget.value.id, grantKey.value, isGranted)
    currentPermissions.value = await getStaffPermissions(permTarget.value.id)
    toast.add({ severity: 'success', summary: isGranted ? '已授予' : '已撤销', life: 2000 })
  } catch (err) {
    toast.add({ severity: 'error', summary: '操作失败', detail: err.response?.data?.detail || '请稍后重试', life: 3000 })
  }
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.perm-tags { display: flex; flex-wrap: wrap; gap: 6px; margin: var(--space-3) 0; }
.perm-tag { font-size: var(--text-xs); background: var(--color-surface-offset); padding: 2px 8px; border-radius: var(--radius-full); }
.perm-grant-row { display: flex; gap: var(--space-2); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); }
</style>
