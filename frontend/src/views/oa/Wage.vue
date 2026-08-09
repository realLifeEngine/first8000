<template>
  <div>
    <PageHeader title="工资明细" crumb="办公OA > 工资明细" subtitle="员工基本工资与奖金发放情况" />
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="name" header="姓名" sortable /><Column field="dept" header="部门" sortable />
        <Column field="base" header="基本工资" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.base).toLocaleString() }}</span></template></Column>
        <Column field="bonus" header="绩效奖金" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.bonus).toLocaleString() }}</span></template></Column>
        <Column field="amount" header="应发合计" sortable><template #body="{ data }"><span class="tabular" style="font-weight:600">¥{{ Number(data.amount).toLocaleString() }}</span></template></Column>
        <Column field="status" header="发放状态" sortable><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
        <Column header="管理" style="width:110px"><template #body="{ data }"><Button v-if="data.status==='待发放'" label="标记发放" size="small" text @click="markPaid(data)" /></template></Column>
      </DataTable>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { wages } from '../../api/oa'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])
const loading = ref(false)

async function loadWages() {
  loading.value = true
  try {
    const data = await wages.list()
    list.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadWages())

async function markPaid(row) {
  try {
    await wages.update(row.id, { ...row, status: '已发放' })
    await loadWages()
    toast.add({ severity: 'success', summary: '已发放', detail: `${row.name} 的工资已标记为发放`, life: 2500 })
  } catch (e) {
    toast.add({ severity: 'error', summary: '操作失败', detail: e.message, life: 3000 })
  }
}
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
</style>
