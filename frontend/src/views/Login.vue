<!--
  views/Login.vue
  Login screen: replaces any hardcoded/mock session with a real call to
  POST /auth/login via the Pinia auth store. On success, redirects to the
  originally requested route (or /app/overview) and lands with the user's
  resolved permissions already loaded for immediate UI gating.
-->
<template>
  <div class="login-page">
    <div class="login-card">
      <h1>启慧教育管理后台</h1>
      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label for="username">用户名</label>
          <InputText id="username" v-model="username" autocomplete="username" :disabled="loading" />
        </div>
        <div class="field">
          <label for="password">密码</label>
          <Password id="password" v-model="password" :feedback="false" toggleMask autocomplete="current-password" :disabled="loading" />
        </div>
        <Message v-if="errorMessage" severity="error" :closable="false">{{ errorMessage }}</Message>
        <Button type="submit" label="登录" class="w-full" :loading="loading" />
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function handleSubmit() {
  errorMessage.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    const redirectTo = route.query.redirect || '/app/overview'
    router.push(redirectTo)
  } catch (err) {
    const detail = err.response?.data?.detail
    if (err.response?.status === 423) {
      errorMessage.value = '账户已被锁定，请稍后再试'
    } else if (err.response?.status === 401) {
      errorMessage.value = '用户名或密码错误'
    } else {
      errorMessage.value = detail || '登录失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-ground, #f4f6f8);
}
.login-card {
  width: 360px;
  padding: 2rem;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}
.login-card h1 {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
.field {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.w-full {
  width: 100%;
}
</style>
