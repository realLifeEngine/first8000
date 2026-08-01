<template>
  <div>
    <PageHeader title="操作记录" crumb="办公OA > 操作记录" subtitle="系统关键数据变更审计日志" />
    <div class="table-card">
      <DataTable :value="list" paginator :rows="12" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="time" header="操作时间" sortable /><Column field="student" header="关联学员" sortable /><Column field="action" header="操作内容" sortable /><Column field="dataType" header="数据类型" sortable />
        <Column field="reason" header="操作原因" /><Column field="auditor" header="操作人" sortable /><Column field="campus" header="所属校区" sortable />
      </DataTable>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { operationLogs } from '../../data/mockData'
const list = ref([...operationLogs])
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
</style>
