<template>
  <div>
    <PageHeader title="课堂点评" crumb="教务管理 > 消课管理 > 课堂点评" subtitle="对已完成课堂进行教学点评">
      <template #actions><Button label="高级搜索" icon="pi pi-filter" outlined @click="showFilter=true" /></template>
    </PageHeader>
    <div class="menu-tabs">
      <button :class="{active: mode==='pending'}" @click="mode='pending'">待评列表 ({{ pending.length }})</button>
      <button :class="{active: mode==='done'}" @click="mode='done'">已评列表 ({{ done.length }})</button>
    </div>
    <div class="table-card">
      <DataTable :value="mode==='pending' ? pending : done" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows>
        <Column field="date" header="日期" sortable /><Column field="student" header="学员" sortable /><Column field="teacher" header="教师" sortable /><Column field="course" header="课程" /><Column field="topic" header="主题" />
        <Column v-if="mode==='done'" field="rating" header="评分"><template #body="{ data }"><Rating :modelValue="data.rating" readonly :cancel="false" /></template></Column>
        <Column header="操作" style="width:120px"><template #body="{ data }"><Button :label="mode==='pending' ? '去点评' : '查看'" size="small" text @click="openReview(data)" /></template></Column>
      </DataTable>
    </div>
    <Dialog v-model:visible="showReview" modal :header="reviewing && reviewing.status === '已评' ? '查看点评' : '课堂点评'" :style="{width:'560px'}">
      <div v-if="reviewing" class="review-body">
        <div class="review-meta"><p><strong>{{ reviewing.student }}</strong> · {{ reviewing.course }} · {{ reviewing.date }}</p><p class="muted">授课教师：{{ reviewing.teacher }} · 主题：{{ reviewing.topic }}</p></div>
        <div class="field"><label>星级评分</label><Rating v-model="reviewing.rating" :cancel="false" :readonly="reviewing.status==='已评'" /></div>
        <div class="field"><label>点评内容</label><Textarea v-model="reviewing.comment" rows="5" autoResize :readonly="reviewing.status==='已评'" placeholder="请填写本次课堂表现、进度与建议..." /></div>
      </div>
      <template #footer><Button label="关闭" severity="secondary" outlined @click="showReview=false" /><Button v-if="reviewing && reviewing.status!=='已评'" label="提交点评" @click="submitReview" /></template>
    </Dialog>
    <RecordDialog v-model:visible="showFilter" title="按条件筛选" width="560px" confirm-label="筛选" @confirm="showFilter=false">
      <div class="form-grid"><div class="field"><label>学员姓名</label><InputText v-model="filterName" /></div><div class="field"><label>授课教师</label><InputText v-model="filterTeacher" /></div></div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import PageHeader from '../../components/PageHeader.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Rating from 'primevue/rating'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import { useToast } from 'primevue/usetoast'
import { listCourseRecords, submitCourseReview } from '../../api/school'
import { normalizeListResponse } from '../../api/response'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])
const loading = ref(false)
const mode = ref('pending')
const pending = computed(() => list.value.filter(r => r.status === '待评'))
const done = computed(() => list.value.filter(r => r.status === '已评'))
const showReview = ref(false)
const reviewing = ref(null)

async function loadCourseRecords() {
  loading.value = true
  try {
    const data = await listCourseRecords()
    list.value = normalizeListResponse(data)
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadCourseRecords())

function openReview(row) { reviewing.value = row; showReview.value = true }

async function submitReview() {
  try {
    await submitCourseReview(reviewing.value.id, { rating: reviewing.value.rating, comment: reviewing.value.comment })
    await loadCourseRecords()
    showReview.value = false
    toast.add({ severity: 'success', summary: '点评已提交', detail: `${reviewing.value.student} 的课堂点评已完成`, life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: '提交失败', detail: e.message, life: 3000 })
  }
}

const showFilter = ref(false)
const filterName = ref('')
const filterTeacher = ref('')
</script>
<style scoped>
.menu-tabs { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); border-bottom: 1px solid var(--color-divider); }
.menu-tabs button { padding: var(--space-2) var(--space-4); font-size: var(--text-sm); color: var(--color-text-muted); border-bottom: 2px solid transparent; }
.menu-tabs button.active { color: var(--color-primary); border-color: var(--color-primary); font-weight: 600; }
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.review-body { display: flex; flex-direction: column; gap: var(--space-4); }
.review-meta { padding-bottom: var(--space-3); border-bottom: 1px solid var(--color-divider); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
</style>
