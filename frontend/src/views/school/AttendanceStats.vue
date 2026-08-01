<template>
  <div>
    <PageHeader title="出勤统计" crumb="教务管理 > 出勤统计" subtitle="按学员维度统计每周出勤与耗课情况" />
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows scrollable scrollHeight="480px">
        <Column field="name" header="学员姓名" sortable frozen />
        <Column field="status" header="业务状态"><template #body="{ data }"><StatusTag :value="data.status" /></template></Column>
        <Column v-for="(d,i) in days" :key="d" :header="d" style="width:56px"><template #body="{ data }"><span class="tabular day-cell">{{ data.week[i] }}</span></template></Column>
        <Column field="regular" header="常规" /><Column field="review" header="点评" /><Column field="pending" header="待补" /><Column field="dept" header="业务部门" />
        <Column header="操作" style="width:90px"><template #body="{ data }"><Button label="查看" size="small" text @click="openDetail(data)" /></template></Column>
      </DataTable>
    </div>
    <Dialog v-model:visible="showDetail" modal header="出勤明细" :style="{width:'480px'}">
      <div v-if="active" class="detail-view">
        <div class="detail-row"><span>学员</span><strong>{{ active.name }}</strong></div>
        <div class="detail-row"><span>本周出勤</span><span class="tabular">{{ active.week.filter(x=>x==='✓').length }} / 7</span></div>
        <div class="detail-row"><span>常规课时</span><span class="tabular">{{ active.regular }}</span></div>
        <div class="detail-row"><span>已点评</span><span class="tabular">{{ active.review }}</span></div>
        <div class="detail-row"><span>待补课</span><span class="tabular">{{ active.pending }}</span></div>
      </div>
      <template #footer><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import StatusTag from '../../components/StatusTag.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import { students } from '../../data/mockData'
const days = ['一','二','三','四','五','六','日']
const list = ref(students.slice(0, 20).map((s, i) => ({
  id: s.id, name: s.name, status: s.status,
  week: Array.from({length:7}, () => (Math.random() > 0.3 ? '✓' : '-')),
  regular: Math.floor(Math.random()*10), review: Math.floor(Math.random()*8),
  pending: Math.floor(Math.random()*3), dept: i % 2 === 0 ? '总校区' : '分校区A',
})))
const showDetail = ref(false)
const active = ref(null)
function openDetail(row) { active.value = row; showDetail.value = true }
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.day-cell { display: block; text-align: center; }
.detail-view { display: flex; flex-direction: column; gap: var(--space-3); }
.detail-row { display: flex; justify-content: space-between; font-size: var(--text-sm); }
.detail-row span:first-child { color: var(--color-text-muted); }
</style>
