<template>
  <div>
    <PageHeader title="业绩统计" crumb="数据中心 > 业绩统计" subtitle="校区维度的签约、退费与净业绩概览">
      <template #actions><Button label="导出报表" icon="pi pi-download" outlined @click="exportReport" /></template>
    </PageHeader>
    <div class="kpi-grid">
      <KpiCard label="总签约金额" :value="'¥' + totalSign.toLocaleString()" :icon="TrendingUp" :delta="6.4" />
      <KpiCard label="总退费金额" :value="'¥' + totalRefund.toLocaleString()" :icon="TrendingDown" accent="var(--color-warning)" :delta="-2.1" />
      <KpiCard label="净业绩" :value="'¥' + totalNet.toLocaleString()" :icon="Wallet" :delta="7.8" />
      <KpiCard label="新增学员" :value="totalNew" :icon="Users" :delta="4.5" />
    </div>
    <div class="table-card">
      <DataTable :value="list" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="campus" header="校区" sortable />
        <Column field="signAmount" header="签约金额" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.signAmount).toLocaleString() }}</span></template></Column>
        <Column field="refundAmount" header="退费金额" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.refundAmount).toLocaleString() }}</span></template></Column>
        <Column field="netAmount" header="净业绩" sortable><template #body="{ data }"><span class="tabular" style="font-weight:600">¥{{ Number(data.netAmount).toLocaleString() }}</span></template></Column>
        <Column field="newStudents" header="新增学员" sortable /><Column field="renewalRate" header="续费率" sortable />
      </DataTable>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { TrendingUp, TrendingDown, Wallet, Users } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import KpiCard from '../../components/KpiCard.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { listRevenue } from '../../api/datacenter'
const toast = useToast()
const list = ref([])
const loading = ref(false)

async function loadRevenue() {
  loading.value = true
  try {
    const data = await listRevenue()
    list.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadRevenue())
const totalSign = computed(() => list.value.reduce((s, c) => s + Number(c.signAmount), 0))
const totalRefund = computed(() => list.value.reduce((s, c) => s + Number(c.refundAmount), 0))
const totalNet = computed(() => list.value.reduce((s, c) => s + Number(c.netAmount), 0))
const totalNew = computed(() => list.value.reduce((s, c) => s + c.newStudents, 0))
function exportReport() { toast.add({ severity: 'info', summary: '导出中', detail: '业绩报表正在生成...', life: 2500 }) }
</script>
<style scoped>
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-6); }
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
</style>
