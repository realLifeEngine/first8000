<template>
  <div>
    <PageHeader title="内部培训" crumb="办公OA > 内部培训" subtitle="团队培训素材与案例学习库" />
    <div class="grid-cards">
      <div v-for="t in list" :key="t.id" class="training-card" @click="openDetail(t)">
        <div class="training-head"><span class="training-type">{{ t.type }}</span><Star v-if="t.starred" :size="14" class="star" /></div>
        <h4>{{ t.title }}</h4><p class="muted">{{ t.teacher }} · {{ t.updateTime }}</p>
        <span class="permission-tag">{{ t.permission }}</span>
      </div>
    </div>
    <Dialog v-model:visible="showDetail" modal header="培训详情" :style="{width:'560px'}">
      <div v-if="active"><h3>{{ active.title }}</h3><p class="muted">{{ active.teacher }} · {{ active.permission }}</p><p class="content-text">{{ active.detail }}</p></div>
      <template #footer><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Star } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { teamLibrary } from '../../data/mockData'
const list = ref([...teamLibrary])
const showDetail = ref(false)
const active = ref(null)
function openDetail(t) { active.value = t; showDetail.value = true }
</script>
<style scoped>
.grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-4); }
.training-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-4); cursor: pointer; box-shadow: var(--shadow-sm); }
.training-card:hover { box-shadow: var(--shadow-md); }
.training-head { display: flex; justify-content: space-between; align-items: center; }
.training-type { font-size: var(--text-xs); color: var(--color-primary); font-weight: 600; }
.star { color: var(--color-warning); }
.training-card h4 { font-size: var(--text-base); margin: var(--space-2) 0; }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); margin-bottom: var(--space-2); }
.permission-tag { font-size: var(--text-xs); background: var(--color-surface-offset); color: var(--color-text-muted); padding: 2px var(--space-2); border-radius: var(--radius-full); }
.content-text { font-size: var(--text-sm); line-height: 1.7; }
</style>
