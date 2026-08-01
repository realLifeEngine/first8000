<template>
  <div>
    <PageHeader title="课程管理" crumb="教务管理 > 课程管理" subtitle="课程产品目录与教学内容维护">
      <template #actions><Button v-if="auth.can('course_product:manage')" label="新增课程" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="grid-cards">
      <div v-for="c in list" :key="c.id" class="course-card" @click="openDetail(c)">
        <div class="course-thumb"><BookOpen :size="28" /></div>
        <div class="course-body">
          <p class="course-seq">课序 {{ c.seq }}</p><h4>{{ c.name }}</h4><p class="course-product">{{ c.product }}</p>
          <div class="course-meta"><Rating :modelValue="c.difficulty" readonly :cancel="false" /><span class="version-tag">{{ c.version }}</span></div>
        </div>
      </div>
    </div>
    <Dialog v-model:visible="showDetail" modal header="课程详情" :style="{width:'560px'}">
      <div v-if="activeCourse" class="detail-body">
        <h3>{{ activeCourse.name }}</h3><p class="muted">{{ activeCourse.product }} · 难度 <Rating :modelValue="activeCourse.difficulty" readonly :cancel="false" style="display:inline-flex" /></p>
        <div class="field"><label>课程信息</label><p>{{ activeCourse.info }}</p></div>
        <div class="field"><label>课程目标</label><p>{{ activeCourse.goal }}</p></div>
      </div>
      <template #footer><Button label="编辑" outlined @click="editFromDetail" /><Button label="关闭" @click="showDetail=false" /></template>
    </Dialog>
    <RecordDialog v-model:visible="showEditor" :title="editing?'编辑课程':'新增课程'" width="600px" @confirm="save">
      <div class="form-grid">
        <div class="field"><label>课程名称</label><InputText v-model="form.name" /></div>
        <div class="field"><label>课程产品</label><InputText v-model="form.product" /></div>
        <div class="field"><label>难度系数</label><Rating v-model="form.difficulty" :cancel="false" /></div>
        <div class="field"><label>版本</label><InputText v-model="form.version" /></div>
        <div class="field full"><label>课程信息</label><Textarea v-model="form.info" rows="3" autoResize /></div>
        <div class="field full"><label>课程目标</label><Textarea v-model="form.goal" rows="3" autoResize /></div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { BookOpen } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Rating from 'primevue/rating'
import { useToast } from 'primevue/usetoast'
import { listCourseProducts, createCourseProduct, updateCourseProduct } from '../../api/school'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])

async function fetchProducts() {
  try {
    const res = await listCourseProducts({ page: 1, page_size: 100 })
    list.value = res.items
  } catch (err) {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取课程列表', life: 3000 })
  }
}
fetchProducts()
const showDetail = ref(false)
const activeCourse = ref(null)
function openDetail(c) { activeCourse.value = c; showDetail.value = true }
function editFromDetail() { showDetail.value = false; openEdit(activeCourse.value) }
const showEditor = ref(false)
const editing = ref(false)
const form = ref({ name: '', product: '', difficulty: 3, version: 'v1.0', info: '', goal: '' })
function openCreate() { editing.value = false; form.value = { name: '', product: '', difficulty: 3, version: 'v1.0', info: '', goal: '' }; showEditor.value = true }
function openEdit(row) { editing.value = true; form.value = { ...row }; showEditor.value = true }
async function save() {
  try {
    if (editing.value) {
      const updated = await updateCourseProduct(form.value.id, form.value)
      const idx = list.value.findIndex(c => c.id === form.value.id)
      if (idx > -1) list.value[idx] = updated
      toast.add({ severity: 'success', summary: '更新成功', life: 2500 })
    } else {
      const created = await createCourseProduct(form.value)
      list.value.unshift(created)
      toast.add({ severity: 'success', summary: '新增成功', life: 2500 })
    }
    showEditor.value = false
  } catch (err) {
    toast.add({ severity: 'error', summary: '操作失败', detail: err.response?.data?.detail || '请稍后重试', life: 3000 })
  }
}
</script>
<style scoped>
.grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-4); }
.course-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); padding: var(--space-4); cursor: pointer; box-shadow: var(--shadow-sm); transition: box-shadow var(--transition-interactive), transform var(--transition-interactive); }
.course-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.course-thumb { width: 100%; height: 96px; border-radius: var(--radius-md); background: var(--color-primary-highlight); color: var(--color-primary); display: flex; align-items: center; justify-content: center; margin-bottom: var(--space-3); }
.course-seq { font-size: var(--text-xs); color: var(--color-text-faint); }
.course-card h4 { font-size: var(--text-base); margin: var(--space-1) 0; }
.course-product { font-size: var(--text-sm); color: var(--color-text-muted); margin-bottom: var(--space-2); }
.course-meta { display: flex; align-items: center; justify-content: space-between; }
.version-tag { font-size: var(--text-xs); color: var(--color-text-faint); font-family: var(--font-mono); }
.detail-body { display: flex; flex-direction: column; gap: var(--space-3); }
.detail-body h3 { font-size: var(--text-lg); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); font-weight: 500; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field.full { grid-column: 1 / -1; }
</style>
