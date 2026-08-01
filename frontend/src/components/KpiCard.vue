<template>
  <div class="kpi-card">
    <div class="kpi-icon" :style="{ color: accent }"><component :is="icon" :size="20" /></div>
    <div class="kpi-body">
      <p class="kpi-label">{{ label }}</p>
      <p class="kpi-value tabular">{{ value }}</p>
      <p v-if="delta !== null" class="kpi-delta" :class="delta >= 0 ? 'up' : 'down'">{{ delta >= 0 ? '↑' : '↓' }} {{ Math.abs(delta) }}%</p>
    </div>
  </div>
</template>
<script setup>
defineProps({ label: String, value: [String, Number], delta: { type: Number, default: null }, icon: [Object, Function], accent: { type: String, default: 'var(--color-primary)' } })
</script>
<style scoped>
.kpi-card { display: flex; gap: var(--space-3); align-items: flex-start; background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-4); box-shadow: var(--shadow-sm); }
.kpi-icon { width: 40px; height: 40px; border-radius: var(--radius-md); background: var(--color-primary-highlight); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.kpi-label { font-size: var(--text-sm); color: var(--color-text-muted); }
.kpi-value { font-size: var(--text-lg); font-weight: 700; margin-top: var(--space-1); }
.kpi-delta { font-size: var(--text-xs); margin-top: var(--space-1); font-weight: 600; }
.kpi-delta.up { color: var(--color-success); }
.kpi-delta.down { color: var(--color-error); }
</style>
