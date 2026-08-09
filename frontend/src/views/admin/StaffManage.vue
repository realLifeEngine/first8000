<template>
  <div>
    <PageHeader title="员工管理" crumb="系统管理 > 员工管理" subtitle="员工账号、角色与权限管理">
      <template #actions><Button label="新增员工" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>

    <div class="summary-card">
      <div>
        <div class="summary-title">人员总览</div>
        <div class="summary-value">{{ list.length }} 位员工</div>
      </div>
      <Button label="新增员工" icon="pi pi-plus" @click="openCreate" />
    </div>

    <div class="table-card">
      <DataTable :value="list" :loading="loading" paginator :rows="8" :rowsPerPageOptions="[8, 12]" dataKey="id" responsiveLayout="scroll" stripedRows showGridlines rowHover>
        <template #empty>
          <div class="empty-state"><i class="pi pi-users" /><span>当前暂无员工信息。</span></div>
        </template>
        <Column field="name" header="姓名" sortable />
        <Column field="username" header="用户名" sortable />
        <Column field="role" header="角色" sortable />
        <Column field="dept" header="部门" />
        <Column field="is_active" header="状态">
          <template #body="{ data }">
            <span class="status-pill" :class="data.is_active ? 'active' : 'inactive'">{{ data.is_active ? '启用' : '禁用' }}</span>
          </template>
        </Column>
        <Column header="操作" style="width:160px">
          <template #body="{ data }">
            <div class="row-actions">
              <button class="icon-action" type="button" aria-label="权限管理" @click="openPermissions(data)"><i class="pi pi-key" /></button>
              <button class="icon-action" type="button" aria-label="编辑员工" @click="openEdit(data)"><i class="pi pi-pencil" /></button>
              <button class="icon-action danger" type="button" aria-label="删除员工" @click="remove(data)"><i class="pi pi-trash" /></button>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
    <RecordDialog v-model:visible="showEditor" :title="editing ? '编辑员工' : '新增员工'" width="560px" @confirm="save">
      <div class="form-grid">
        <div class="field">
          <label>姓名</label>
          <InputText v-model="form.name" :invalid="!!formErrors.name" @input="clearFieldError('name')" />
          <small v-if="formErrors.name" class="field-error">{{ formErrors.name }}</small>
        </div>
        <div class="field">
          <label>用户名</label>
          <InputText v-model="form.username" :disabled="editing" :invalid="!!formErrors.username" @input="clearFieldError('username')" />
          <small v-if="formErrors.username" class="field-error">{{ formErrors.username }}</small>
        </div>
        <div v-if="!editing" class="field">
          <label>初始密码</label>
          <Password v-model="form.password" :feedback="false" toggleMask :invalid="!!formErrors.password" @input="clearFieldError('password')" />
          <small v-if="formErrors.password" class="field-error">{{ formErrors.password }}</small>
        </div>
        <div class="field">
          <label>角色</label>
          <Dropdown v-model="form.role" :options="['teacher','manager','school_admin','superuser']" :invalid="!!formErrors.role" @change="clearFieldError('role')" />
          <small v-if="formErrors.role" class="field-error">{{ formErrors.role }}</small>
        </div>
        <div class="field">
          <label>所属校区</label>
          <Dropdown
            v-model="form.branch_id"
            :options="branches"
            optionLabel="label"
            optionValue="value"
            :disabled="editing"
            placeholder="请选择校区"
            :invalid="!!formErrors.branch_id"
            appendTo="body"
            @change="clearFieldError('branch_id')"
          />
          <small v-if="formErrors.branch_id" class="field-error">{{ formErrors.branch_id }}</small>
        </div>
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
import { storeToRefs } from 'pinia'
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
import { listBranches } from '../../api/branches'
import { listStaff, createStaff, updateStaff, deleteStaff, getStaffPermissions, setStaffPermission } from '../../api/staff'
import { useAuthStore } from '../../stores/auth'

const toast = useToast()
const confirm = useConfirm()
const auth = useAuthStore()
const { user } = storeToRefs(auth)
const list = ref([])
const loading = ref(false)
const branches = ref([])

async function fetchBranches() {
  try {
    const res = await listBranches({ page: 1, page_size: 100 })
    branches.value = (res.items || []).map((branch) => ({ label: branch.name, value: branch.id }))
  } catch {
    branches.value = []
    toast.add({ severity: 'error', summary: '校区加载失败', detail: '无法获取校区列表', life: 3000 })
  }
}

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
fetchBranches()

const showEditor = ref(false)
const editing = ref(false)
const form = ref({ name: '', username: '', password: '', role: 'teacher', dept: '', branch_id: '' })
const formErrors = ref({ name: '', username: '', password: '', role: '', branch_id: '' })

function resetFormErrors() {
  formErrors.value = { name: '', username: '', password: '', role: '', branch_id: '' }
}

function clearFieldError(field) {
  formErrors.value[field] = ''
}

function validateForm() {
  resetFormErrors()
  const name = String(form.value.name || '').trim()
  const username = String(form.value.username || '').trim()
  const password = String(form.value.password || '')

  if (!name) formErrors.value.name = '请输入姓名'
  if (!form.value.role) formErrors.value.role = '请选择角色'

  if (!editing.value) {
    if (username.length < 3) formErrors.value.username = '用户名至少 3 位'
    if (password.length < 6) formErrors.value.password = '密码至少 6 位'
    if (!form.value.branch_id) formErrors.value.branch_id = '请选择所属校区'
  }

  return !Object.values(formErrors.value).some(Boolean)
}

async function openCreate() {
  await fetchBranches()
  editing.value = false
  resetFormErrors()
  form.value = {
    name: '',
    username: '',
    password: '',
    role: 'teacher',
    dept: '',
    branch_id: user.value?.branchId || '',
  }
  if (!branches.value.length) {
    toast.add({ severity: 'warn', summary: '暂无可选校区', detail: '请先创建校区后再新增员工', life: 3000 })
  }
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
    const username = String(form.value.username || '').trim()
    const password = String(form.value.password || '')
    const dept = String(form.value.dept || '').trim()

    if (editing.value) {
      const updated = await updateStaff(form.value.id, {
        name,
        role: form.value.role,
        dept: dept || null,
      })
      const idx = list.value.findIndex(s => s.id === form.value.id)
      if (idx > -1) list.value[idx] = updated
      toast.add({ severity: 'success', summary: '更新成功', life: 2500 })
    } else {
      const created = await createStaff({
        name,
        username,
        password,
        role: form.value.role,
        dept: dept || null,
        branch_id: form.value.branch_id,
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
.status-pill { display: inline-flex; align-items: center; padding: 2px var(--space-2); border-radius: 999px; font-size: var(--text-xs); font-weight: 600; }
.status-pill.active { background: var(--color-success-highlight); color: var(--color-success); }
.status-pill.inactive { background: var(--color-error-highlight); color: var(--color-error); }
.empty-state { display: flex; align-items: center; justify-content: center; gap: var(--space-2); padding: var(--space-5); color: var(--color-text-muted); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.field-error { color: var(--color-error); font-size: var(--text-xs); line-height: 1.2; }
.perm-tags { display: flex; flex-wrap: wrap; gap: 6px; margin: var(--space-3) 0; }
.perm-tag { font-size: var(--text-xs); background: var(--color-surface-offset); padding: 2px 8px; border-radius: var(--radius-full); }
.perm-grant-row { display: flex; gap: var(--space-2); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); }
</style>
