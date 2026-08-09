<template>
  <div>
    <PageHeader title="站内短信" crumb="办公OA > 站内短信" subtitle="内部即时消息与通知提醒" />
    <div class="msg-list">
      <div v-for="m in list" :key="m.id" class="msg-item" :class="{unread: !m.read}" @click="markRead(m)">
        <Avatar :label="displaySender(m).charAt(0)" shape="circle" size="normal" />
        <div class="msg-body"><p class="msg-title">{{ m.title || '未命名消息' }}</p><p class="msg-meta">{{ displaySender(m) }} · {{ m.time || m.createTime || '-' }}</p></div>
        <span v-if="!m.read" class="unread-dot"></span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import Avatar from 'primevue/avatar'
import { useToast } from 'primevue/usetoast'
import { messages as messagesApi } from '../../api/oa'
const toast = useToast()
const list = ref([])
const loading = ref(false)

async function loadMessages() {
  loading.value = true
  try {
    const data = await messagesApi.list()
    list.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadMessages())
function displaySender(m) { return m.sender || m.senderName || m.publisher || '系统' }
function markRead(m) { m.read = true }
</script>
<style scoped>
.msg-list { display: flex; flex-direction: column; gap: var(--space-2); }
.msg-item { display: flex; align-items: center; gap: var(--space-3); background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-4); cursor: pointer; box-shadow: var(--shadow-sm); }
.msg-item.unread { background: var(--color-primary-highlight); }
.msg-body { flex: 1; }
.msg-title { font-size: var(--text-sm); font-weight: 500; }
.msg-meta { font-size: var(--text-xs); color: var(--color-text-muted); margin-top: 2px; }
.unread-dot { width: 8px; height: 8px; border-radius: var(--radius-full); background: var(--color-primary); flex-shrink: 0; }
</style>
