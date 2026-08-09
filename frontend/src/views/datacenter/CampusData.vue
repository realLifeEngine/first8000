<template>
  <div>
    <PageHeader title="校区数据" crumb="数据中心 > 校区数据" subtitle="多校区运营核心指标对比" />
    <div class="grid-cards">
      <div v-for="c in list" :key="c.id" class="campus-card">
        <div class="campus-head"><Building2 :size="20" /><h4>{{ c.campus }}</h4></div>
        <div class="campus-metrics">
          <div><span class="muted">净业绩</span><p class="tabular">¥{{ Number(c.netAmount).toLocaleString() }}</p></div>
          <div><span class="muted">新增学员</span><p class="tabular">{{ c.newStudents }}</p></div>
          <div><span class="muted">续费率</span><p class="tabular">{{ c.renewalRate }}</p></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { Building2 } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import { useToast } from 'primevue/usetoast'
import { listRevenue } from '../../api/datacenter'
const toast = useToast()
const list = ref([])
const loading = ref(false)

async function loadCampusData() {
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

onMounted(() => loadCampusData())
</script>
<style scoped>
.grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-4); }
.campus-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-5); box-shadow: var(--shadow-sm); }
.campus-head { display: flex; align-items: center; gap: var(--space-2); color: var(--color-primary); margin-bottom: var(--space-4); }
.campus-head h4 { font-size: var(--text-base); color: var(--color-text); }
.campus-metrics { display: flex; flex-direction: column; gap: var(--space-3); }
.muted { font-size: var(--text-xs); color: var(--color-text-muted); }
.campus-metrics p { font-weight: 600; margin-top: 2px; }
</style>
