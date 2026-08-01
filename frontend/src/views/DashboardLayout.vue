<!--
  views/DashboardLayout.vue
  Shell layout for all authenticated /app/* routes: top bar showing the
  current user + logout, and a router-view outlet. Sidebar navigation
  should be restored from the original design; this scaffold focuses on
  the auth-integration wiring introduced in Batch 7.
-->
<template>
  <div class="dashboard-layout">
    <header class="topbar">
      <span class="brand">启慧教育管理后台</span>
      <div class="user-info">
        <span>{{ auth.user?.name }} · {{ roleLabel }}</span>
        <Button label="退出登录" text size="small" @click="handleLogout" />
      </div>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import { useAuthStore } from '../stores/auth'

const ROLE_LABELS = {
  teacher: '教师',
  manager: '主管',
  school_admin: '校区管理员',
  superuser: '超级管理员',
}

const auth = useAuthStore()
const router = useRouter()
const roleLabel = computed(() => ROLE_LABELS[auth.role] || auth.role)

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: #fff;
  border-bottom: 1px solid var(--surface-border, #e5e7eb);
}
.brand {
  font-weight: 600;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.content {
  flex: 1;
  padding: 1.5rem;
}
</style>
