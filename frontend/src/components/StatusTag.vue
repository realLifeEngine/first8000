<template><span class="status-tag" :class="cls">{{ value }}</span></template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ value: String })
const cls = computed(() => {
  const positive = ['正常', '已读', '已完成', '已评', '已批准', '已发放']
  const warning = ['意向', '待评', '审批中', '待发放', '未读', '进行中']
  const negative = ['停课', '流失', '已报废', '已拒绝']
  if (positive.includes(props.value)) return 'positive'
  if (warning.includes(props.value)) return 'warning'
  if (negative.includes(props.value)) return 'negative'
  return 'neutral'
})
</script>
<style scoped>
.status-tag { display: inline-flex; align-items: center; padding: 12px var(--space-2); border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: 600; white-space: nowrap; }
.status-tag.positive { background: var(--color-success-highlight); color: var(--color-success); }
.status-tag.warning { background: var(--color-warning-highlight); color: var(--color-warning); }
.status-tag.negative { background: var(--color-error-highlight); color: var(--color-error); }
.status-tag.neutral { background: var(--color-surface-offset); color: var(--color-text-muted); }
</style>
