<template>
  <div class="shell">
    <aside class="sidebar" :class="{ open: mobileOpen }">
      <div class="sidebar-head">
        <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="10" fill="var(--color-primary)"/>
          <path d="M12 26 L20 12 L28 26" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="20" cy="26" r="2.5" fill="white"/>
        </svg>
        <span>启慧教育 CRM</span>
        <button class="close-btn" @click="mobileOpen=false" aria-label="关闭菜单"><X :size="18" /></button>
      </div>
      <nav class="nav">
        <div v-for="group in nav" :key="group.label" class="nav-group">
          <p class="nav-group-label">{{ group.label }}</p>
          <router-link v-for="item in group.items" :key="item.to" :to="item.to" class="nav-item" active-class="active" @click="mobileOpen=false">
            <component :is="item.icon" :size="17" />
            <span>{{ item.label }}</span>
          </router-link>
        </div>
      </nav>
    </aside>
    <div class="overlay" v-if="mobileOpen" @click="mobileOpen=false"></div>
    <div class="main">
      <header class="topbar">
        <button class="menu-btn" @click="mobileOpen=true" aria-label="打开菜单"><Menu :size="20" /></button>
        <div class="topbar-crumb">{{ route.meta.crumb || '' }}</div>
        <div class="topbar-actions">
          <button class="icon-btn" @click="toggleTheme" :aria-label="theme==='dark' ? '切换到浅色模式' : '切换到深色模式'">
            <Sun v-if="theme==='dark'" :size="18" />
            <Moon v-else :size="18" />
          </button>
          <div class="user-chip" @click="showUserMenu = !showUserMenu">
            <Avatar label="管" shape="circle" size="normal" />
            <span class="user-name">管理员</span>
            <ChevronDown :size="14" />
          </div>
          <div v-if="showUserMenu" class="user-menu" v-click-outside>
            <button @click="logout"><LogOut :size="15" /> 退出登录</button>
          </div>
        </div>
      </header>
      <main class="content"><router-view /></main>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, X, Sun, Moon, ChevronDown, LogOut, LayoutDashboard, Users, School, ClipboardList, Star, BookOpen, CalendarCheck, FileText, ListTodo, FileBarChart, Contact, DoorOpen, Package, Wallet, BookMarked, GraduationCap, FolderKanban, MessageSquare, History, TrendingUp, Trophy, Gift, Building2 } from 'lucide-vue-next'
import Avatar from 'primevue/avatar'
const route = useRoute()
const router = useRouter()
const mobileOpen = ref(false)
const showUserMenu = ref(false)
const theme = ref(document.documentElement.getAttribute('data-theme') || 'light')
function toggleTheme() { theme.value = theme.value === 'dark' ? 'light' : 'dark'; document.documentElement.setAttribute('data-theme', theme.value) }
function logout() { showUserMenu.value = false; router.push('/login') }
const vClickOutside = { mounted(el) {
  el._outsideHandler = (e) => { if (!el.contains(e.target)) showUserMenu.value = false }
  document.addEventListener('click', el._outsideHandler)
}, unmounted(el) { document.removeEventListener('click', el._outsideHandler) } }
const nav = [
  { label: '总览', items: [ { to: '/app/overview', label: '仪表盘', icon: LayoutDashboard } ] },
  { label: '前台业务', items: [ { to: '/app/frontdesk/members', label: '会员管理', icon: Users } ] },
  { label: '教务管理', items: [
    { to: '/app/school/class', label: '班级管理', icon: School },
    { to: '/app/school/course-records', label: '教课记录', icon: ClipboardList },
    { to: '/app/school/course-review', label: '课堂点评', icon: Star },
    { to: '/app/school/course-products', label: '课程管理', icon: BookOpen },
    { to: '/app/school/attendance', label: '出勤统计', icon: CalendarCheck },
  ] },
  { label: '办公OA', items: [
    { to: '/app/oa/notices', label: '内部公文', icon: FileText },
    { to: '/app/oa/plans', label: '工作计划', icon: ListTodo },
    { to: '/app/oa/reports', label: '工作报告', icon: FileBarChart },
    { to: '/app/oa/contacts', label: '通讯录', icon: Contact },
    { to: '/app/oa/goout', label: '请假条', icon: DoorOpen },
    { to: '/app/oa/property', label: '资产管理', icon: Package },
    { to: '/app/oa/wage', label: '工资明细', icon: Wallet },
    { to: '/app/oa/knowledge', label: '知识库', icon: BookMarked },
    { to: '/app/oa/training', label: '内部培训', icon: GraduationCap },
    { to: '/app/oa/documents', label: '文件柜', icon: FolderKanban },
    { to: '/app/oa/messages', label: '站内短信', icon: MessageSquare },
    { to: '/app/oa/logs', label: '操作记录', icon: History },
  ] },
  { label: '数据中心', items: [
    { to: '/app/data/revenue', label: '业绩统计', icon: TrendingUp },
    { to: '/app/data/ranking', label: '人员排名', icon: Trophy },
    { to: '/app/data/bonus', label: '奖金汇总', icon: Gift },
    { to: '/app/data/campus', label: '校区数据', icon: Building2 },
  ] },
]
</script>
<style scoped>
.shell { display: flex; min-height: 100dvh; }
.sidebar { width: 260px; background: var(--color-surface); border-right: 1px solid var(--color-divider); display: flex; flex-direction: column; position: fixed; inset: 0 auto 0 0; z-index: 40; transform: translateX(-100%); transition: transform var(--transition-interactive); }
.sidebar.open { transform: translateX(0); }
@media (min-width: 1024px) { .sidebar { position: static; transform: none; } }
.sidebar-head { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-4); border-bottom: 1px solid var(--color-divider); font-weight: 700; font-size: var(--text-sm); }
.close-btn { margin-left: auto; display: flex; }
@media (min-width: 1024px) { .close-btn { display: none; } }
.nav { flex: 1; overflow-y: auto; padding: var(--space-3); }
.nav-group { margin-bottom: var(--space-4); }
.nav-group-label { font-size: var(--text-xs); color: var(--color-text-faint); padding: var(--space-2) var(--space-3); text-transform: uppercase; letter-spacing: 0.04em; }
.nav-item { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-3); border-radius: var(--radius-md); font-size: var(--text-sm); color: var(--color-text-muted); text-decoration: none; }
.nav-item:hover { background: var(--color-surface-offset); color: var(--color-text); }
.nav-item.active { background: var(--color-primary-highlight); color: var(--color-primary); font-weight: 600; }
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 30; }
@media (min-width: 1024px) { .overlay { display: none; } }
.main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.topbar { height: 60px; display: flex; align-items: center; gap: var(--space-3); padding: 0 var(--space-4); border-bottom: 1px solid var(--color-divider); background: var(--color-surface); position: sticky; top: 0; z-index: 20; }
.menu-btn { display: flex; }
@media (min-width: 1024px) { .menu-btn { display: none; } }
.topbar-crumb { flex: 1; font-size: var(--text-sm); color: var(--color-text-muted); }
.topbar-actions { display: flex; align-items: center; gap: var(--space-3); position: relative; }
.icon-btn { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: var(--radius-md); color: var(--color-text-muted); }
.icon-btn:hover { background: var(--color-surface-offset); }
.user-chip { display: flex; align-items: center; gap: var(--space-2); cursor: pointer; padding: var(--space-1) var(--space-2); border-radius: var(--radius-md); }
.user-chip:hover { background: var(--color-surface-offset); }
.user-name { font-size: var(--text-sm); }
.user-menu { position: absolute; top: 48px; right: 0; background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-md); box-shadow: var(--shadow-md); min-width: 140px; overflow: hidden; }
.user-menu button { display: flex; align-items: center; gap: var(--space-2); width: 100%; padding: var(--space-3); font-size: var(--text-sm); }
.user-menu button:hover { background: var(--color-surface-offset); }
.content { padding: var(--space-6); flex: 1; max-width: var(--content-default); margin: 0 auto; width: 100%; }
@media (max-width: 640px) { .content { padding: var(--space-4); } }
</style>
