<template>
  <div class="page-header">
    <div>
      <p class="crumb">{{ crumb }}</p>
      <h1>{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div class="actions"><slot name="actions" /></div>
  </div>
</template>
<script setup>
defineProps({ title: String, crumb: String, subtitle: String })
</script>
<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); margin-bottom: var(--space-6); flex-wrap: wrap; }
.crumb { font-size: var(--text-xs); color: var(--color-text-faint); margin-bottom: var(--space-1); }
h1 { font-size: var(--text-xl); font-weight: 700; }
.subtitle { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: var(--space-1); }
.actions { display: flex; gap: var(--space-2); flex-wrap: wrap; }
@media (max-width: 640px) { .page-header { flex-direction: column; } .actions { width: 100%; } }
</style>
