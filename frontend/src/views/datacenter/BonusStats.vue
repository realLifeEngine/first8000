<template>
  <div>
    <PageHeader title="奖金汇总" crumb="数据中心 > 奖金汇总" subtitle="教师课评奖金与绩效奖金核算">
      <template #actions><Button label="批量发放" icon="pi pi-check" @click="payAll" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="name" header="姓名" sortable /><Column field="dept" header="部门" sortable /><Column field="classHours" header="课时数" sortable />
        <Column field="reviewBonus" header="课评奖金" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.reviewBonus).toLocaleString() }}</span></template></Column>
        <Column field="performanceBonus" header="绩效奖金" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.performanceBonus).toLocaleString() }}</span></template></Column>
        <Column field="totalBonus" header="奖金合计" sortable><template #body="{ data }"><span class="tabular" style="font-weight:600">¥{{ Number(data.totalBonus).toLocaleString() }}</span></template></Column>
        <Column field="status" header="发放状态" sortable><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
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
import { fetchBonusSummary } from '../../api/datacenter'
const toast = useToast()
const list = ref([])
const loading = ref(false)

async function loadBonusStats() {
  loading.value = true
  try {
    const data = await fetchBonusSummary()
    list.value = Array.isArray(data) ? data : data.data || []
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadBonusStats())
function payAll() { list.value.forEach(r => r.status = '已发放'); toast.add({ severity: 'success', summary: '发放完成', detail: '全部待发放奖金已标记发放', life: 2500 }) }
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
</style>
