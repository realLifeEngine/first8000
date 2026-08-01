<template>
  <div>
    <PageHeader title="通讯录" crumb="办公OA > 通讯录" subtitle="快速查找团队成员联系方式" />
    <div class="grid-cards">
      <div v-for="c in contacts" :key="c.id" class="contact-card" @click="openDetail(c)">
        <Avatar :label="c.name.charAt(0)" shape="circle" size="xlarge" />
        <div class="contact-body"><h4>{{ c.name }}</h4><p class="role">{{ c.role }}</p><p class="phone tabular">{{ c.phone }}</p></div>
      </div>
    </div>
    <Dialog v-model:visible="showDetail" modal header="联系人详情" :style="{width:'480px'}">
      <div v-if="active" class="detail-panel">
        <Avatar :label="active.name.charAt(0)" shape="circle" size="xlarge" />
        <h3>{{ active.name }} <span class="nickname">({{ active.nickname }})</span></h3>
        <p class="muted">{{ active.role }} · {{ active.dept }}</p>
        <p class="phone-large tabular">{{ active.phone }}</p>
        <p class="bio">{{ active.bio }}</p>
      </div>
      <template #footer><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import Avatar from 'primevue/avatar'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import { contacts } from '../../data/mockData'
const showDetail = ref(false)
const active = ref(null)
function openDetail(c) { active.value = c; showDetail.value = true }
</script>
<style scoped>
.grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--space-4); }
.contact-card { display: flex; align-items: center; gap: var(--space-3); background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-4); cursor: pointer; box-shadow: var(--shadow-sm); }
.contact-card:hover { box-shadow: var(--shadow-md); }
.contact-body h4 { font-size: var(--text-base); }
.role { font-size: var(--text-sm); color: var(--color-text-muted); }
.phone { font-size: var(--text-xs); color: var(--color-text-faint); margin-top: var(--space-1); }
.detail-panel { display: flex; flex-direction: column; align-items: center; text-align: center; gap: var(--space-2); }
.detail-panel h3 { font-size: var(--text-lg); margin-top: var(--space-2); }
.nickname { color: var(--color-text-muted); font-size: var(--text-sm); font-weight: 400; }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); }
.phone-large { font-size: var(--text-base); font-weight: 600; margin-top: var(--space-2); }
.bio { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: var(--space-2); }
</style>
