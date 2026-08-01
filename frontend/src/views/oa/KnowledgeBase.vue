<template>
  <div>
    <PageHeader title="知识库" crumb="办公OA > 知识库" subtitle="常见问题与标准话术查阅" />
    <div class="grid-cards">
      <div v-for="k in list" :key="k.id" class="kb-card" @click="openDetail(k)">
        <span class="kb-type">{{ k.type }}</span><h4>{{ k.qa }}</h4><p class="kb-date">更新于 {{ k.updateTime }}</p>
      </div>
    </div>
    <Dialog v-model:visible="showDetail" modal header="知识详情" :style="{width:'560px'}">
      <div v-if="active"><h3>{{ active.qa }}</h3><p class="muted">{{ active.type }} · 更新于 {{ active.updateTime }}</p><p class="content-text">{{ active.content }}</p></div>
      <template #footer><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { knowledgeBase } from '../../data/mockData'
const list = ref([...knowledgeBase])
const showDetail = ref(false)
const active = ref(null)
function openDetail(k) { active.value = k; showDetail.value = true }
</script>
<style scoped>
.grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-4); }
.kb-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-4); cursor: pointer; box-shadow: var(--shadow-sm); }
.kb-card:hover { box-shadow: var(--shadow-md); }
.kb-type { font-size: var(--text-xs); color: var(--color-primary); font-weight: 600; }
.kb-card h4 { font-size: var(--text-base); margin: var(--space-2) 0; }
.kb-date { font-size: var(--text-xs); color: var(--color-text-faint); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); margin-bottom: var(--space-3); }
.content-text { font-size: var(--text-sm); line-height: 1.7; }
</style>
