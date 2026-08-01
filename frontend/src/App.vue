<template>
  <router-view />
  <Toast position="top-right" />
  <ConfirmDialog />
</template>
<script setup>
import { onMounted } from 'vue'
onMounted(() => {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
})
</script>
