<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="brand">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none" aria-label="启慧教育Logo">
          <rect width="40" height="40" rx="10" fill="var(--color-primary)"/>
          <path d="M12 26 L20 12 L28 26" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="20" cy="26" r="2.5" fill="white"/>
        </svg>
        <h1>启慧教育 CRM</h1>
      </div>
      <p class="tagline">连接教务、行政与数据，一站式教育机构运营中枢</p>
      <ul class="feature-list" role="list">
        <li>会员全生命周期精细化管理</li>
        <li>教务排课与消课点评一体化</li>
        <li>行政办公与业绩数据实时联动</li>
      </ul>
    </div>
    <div class="form-panel">
      <div class="form-card">
        <h2>登录控制台</h2>
        <p class="muted">使用您的账号密码登录系统</p>
        <div class="field">
          <label for="u">用户名</label>
          <InputText id="u" v-model="username" placeholder="请输入用户名" @keyup.enter="login" />
        </div>
        <div class="field">
          <label for="p">密码</label>
          <Password id="p" v-model="password" placeholder="请输入密码" :feedback="false" toggleMask @keyup.enter="login" />
        </div>
        <Button label="登 录" class="login-btn" @click="login" />
        <p class="hint">演示环境：任意用户名密码即可登录</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '../stores/auth'
import { initTheme } from '../utils/theme'
const router = useRouter()
const route = useRoute()
const toast = useToast()
const auth = useAuthStore()
const username = ref('')
const password = ref('')

async function login() {
  try {
    await auth.login(username.value, password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/app/school/class'
    await router.push(redirect)
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: '登录失败',
      detail: e?.response?.data?.detail || e?.message || '账号或密码错误',
      life: 3000,
    })
  }
}

onMounted(() => {
  initTheme('light')
})
</script>
<style scoped>
.login-page { display: grid; grid-template-columns: 1fr; min-height: 100dvh; }
@media (min-width: 900px) { .login-page { grid-template-columns: 1.1fr 1fr; } }
.login-panel { background: linear-gradient(160deg, var(--color-primary-active), var(--color-primary)); color: #fff; padding: var(--space-16) var(--space-10); display: none; flex-direction: column; justify-content: center; gap: var(--space-6); }
@media (min-width: 900px) { .login-panel { display: flex; } }
.brand { display: flex; align-items: center; gap: var(--space-3); }
.brand h1 { font-size: var(--text-lg); font-weight: 700; }
.tagline { font-size: var(--text-lg); font-weight: 500; max-width: 28ch; }
.feature-list { display: flex; flex-direction: column; gap: var(--space-3); font-size: var(--text-sm); opacity: 0.9; }
.feature-list li::before { content: '✓ '; margin-right: var(--space-1); }
.form-panel { display: flex; align-items: center; justify-content: center; padding: var(--space-8); }
.form-card { width: 100%; max-width: 380px; display: flex; flex-direction: column; gap: var(--space-4); }
.form-card h2 { font-size: var(--text-xl); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); margin-bottom: var(--space-2); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.login-btn { margin-top: var(--space-2); height: 44px; }
.hint { font-size: var(--text-xs); color: var(--color-text-faint); text-align: center; margin-top: var(--space-2); }
:deep(.p-password input) { width: 100%; }
</style>
