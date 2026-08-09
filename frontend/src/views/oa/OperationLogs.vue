<template>
  <div>
    <PageHeader title="操作记录" crumb="办公OA > 操作记录" subtitle="系统关键数据变更审计日志" />
    <div class="table-card">
      <DataTable :value="list" :loading="loading" paginator :rows="12" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="time" header="操作时间" sortable />
        <Column field="module" header="模块" sortable />
        <Column field="action" header="操作内容" sortable />
        <Column field="detail" header="详情" />
        <Column field="actor" header="操作人" sortable />
        <Column field="role" header="角色" sortable />
        <Column field="ip" header="IP" sortable />
        <Column field="branchId" header="校区ID" sortable />
      </DataTable>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useToast } from 'primevue/usetoast'
import { operationLogs as logsApi } from '../../api/oa'
const toast = useToast()
const list = ref([])
const loading = ref(false)

async function loadOperationLogs() {
  loading.value = true
  try {
    const data = await logsApi.list()
    list.value = data.map((item) => ({
      ...item,
      time: item.created_at ? String(item.created_at).replace('T', ' ').slice(0, 19) : '-',
      actor: item.actor_name || item.user_id || '-',
      role: item.actor_role || '-',
      branchId: item.branch_id || '-',
      module: item.module || '-',
      detail: item.detail || '-',
      ip: item.ip || '-',
    }))
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadOperationLogs())
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
</style>
