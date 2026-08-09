<template>
  <div>
    <PageHeader title="公海" crumb="教务管理 > 公海" subtitle="已删除学员回收站，可恢复到会员管理" />

    <div class="table-card">
      <DataTable
        :value="list"
        :loading="loading"
        paginator
        :rows="8"
        :rowsPerPageOptions="[8, 12, 20]"
        dataKey="id"
        responsiveLayout="scroll"
        stripedRows
        showGridlines
        rowHover
      >
        <template #empty>
          <div class="empty-state">
            <i class="pi pi-replay" />
            <span>公海 当前为空。</span>
          </div>
        </template>

        <Column field="name" header="学员姓名" sortable />
        <Column field="gender" header="性别" sortable />
        <Column field="age" header="年龄" sortable />
        <Column field="status" header="状态" sortable />
        <Column field="classInfo" header="班级" sortable />
        <Column field="counselor" header="学管老师" sortable />
        <Column field="phone" header="联系电话" />
        <Column field="deletedAt" header="删除时间" sortable />
        <Column header="操作" style="width: 140px">
          <template #body="{ data }">
            <Button
              label="恢复"
              icon="pi pi-undo"
              size="small"
              :disabled="!auth.can('student:create')"
              @click="restore(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { listPublicFieldStudents, restorePublicFieldStudent } from '../../api/students'
import { useAuthStore } from '../../stores/auth'

const toast = useToast()
const auth = useAuthStore()
const loading = ref(false)
const list = ref([])

async function loadPublicField() {
  loading.value = true
  try {
    list.value = await listPublicFieldStudents()
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message || '无法获取 public_field 数据', life: 3000 })
  } finally {
    loading.value = false
  }
}

async function restore(row) {
  try {
    await restorePublicFieldStudent(row.id)
    toast.add({ severity: 'success', summary: '恢复成功', detail: `学员 ${row.name} 已恢复`, life: 3000 })
    await loadPublicField()
  } catch (e) {
    toast.add({ severity: 'error', summary: '恢复失败', detail: e.message || '请稍后重试', life: 3000 })
  }
}

onMounted(() => {
  loadPublicField()
})
</script>

<style scoped>
.table-card {
  background: var(--color-surface);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-5);
  color: var(--color-text-muted);
}
</style>
