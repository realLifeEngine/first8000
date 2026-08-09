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
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
  padding: var(--space-4) 0 var(--space-3);
  border-bottom: 1px solid var(--color-divider);
  flex-wrap: wrap;
}
.crumb {
  font-size: var(--text-xs);
  color: var(--color-text-faint);
  margin-bottom: var(--space-1);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
h1 {
  font-size: clamp(1.2rem, 2.2vw, 1.6rem);
  font-weight: 700;
  color: var(--color-text);
}
.subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
  max-width: 56ch;
}
.actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  align-items: center;
}
@media (max-width: 640px) {
  .page-header { flex-direction: column; padding-bottom: var(--space-4); }
  .actions { width: 100%; }
  .actions :deep(.p-button) { flex: 1; justify-content: center; }
}
</style>
