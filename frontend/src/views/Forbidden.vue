<!-- views/Forbidden.vue — shown when a route guard blocks navigation due to insufficient role/permission. -->
<template>
  <div class="forbidden-page">
    <h1>403</h1>
    <p>您没有权限访问该页面</p>
    <Button label="返回首页" @click="$router.push('/app/overview')" />
  </div>
</template>

<script setup>
import Button from 'primevue/button'
</script>

<style scoped>
.forbidden-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}
.forbidden-page h1 {
  font-size: 3rem;
  margin: 0;
}
</style>
