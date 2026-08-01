<template>
  <div>
    <PageHeader title="人员排名" crumb="数据中心 > 人员排名" subtitle="教师业绩、出勤与课评数量排名榜" />
    <div class="table-card">
      <DataTable :value="ranked" dataKey="id" responsiveLayout="scroll" stripedRows>
        <Column header="排名" style="width:70px"><template #body="{ index }"><span class="rank-badge" :class="{top: index < 3}">{{ index + 1 }}</span></template></Column>
        <Column field="name" header="姓名" sortable /><Column field="role" header="角色" sortable />
        <Column field="performance" header="业绩" sortable><template #body="{ data }"><span class="tabular">¥{{ Number(data.performance).toLocaleString() }}</span></template></Column>
        <Column field="attendanceRate" header="出勤率" sortable /><Column field="reviewCount" header="课评数量" sortable />
      </DataTable>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { staffRanking } from '../../data/mockData'
const list = ref([...staffRanking])
const ranked = computed(() => [...list.value].sort((a, b) => Number(b.performance) - Number(a.performance)))
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.rank-badge { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: var(--radius-full); background: var(--color-surface-offset); color: var(--color-text-muted); font-weight: 700; font-size: var(--text-xs); }
.rank-badge.top { background: var(--color-gold-highlight); color: var(--color-gold); }
</style>
