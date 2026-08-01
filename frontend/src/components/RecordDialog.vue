<template>
  <Dialog :visible="visible" @update:visible="$emit('update:visible', $event)" modal :header="title" :style="{ width: width }" :breakpoints="{ '960px': '90vw' }">
    <slot />
    <template #footer>
      <Button label="取消" severity="secondary" outlined @click="$emit('update:visible', false)" />
      <Button :label="confirmLabel" @click="$emit('confirm')" />
    </template>
  </Dialog>
</template>
<script setup>
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
defineProps({ visible: Boolean, title: String, width: { type: String, default: '560px' }, confirmLabel: { type: String, default: '保存' } })
defineEmits(['update:visible', 'confirm'])
</script>
