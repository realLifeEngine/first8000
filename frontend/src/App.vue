<template>
  <router-view />
  <Toast position="top-right" />
  <ConfirmDialog />
</template>
<script setup>
import { onMounted } from 'vue'
import { initTheme } from './utils/theme'
onMounted(() => {
  initTheme('light')
})
</script>
