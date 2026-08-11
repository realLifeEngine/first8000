<template>
  <div>
    <PageHeader title="课程管理" crumb="教务管理 > 课程管理" subtitle="课程产品目录与教学内容维护">
      <template #actions><Button label="新增课程" icon="pi pi-plus" @click="openCreate" /></template>
    </PageHeader>
    <div class="grid-cards">
      <div v-for="c in list" :key="c.id" class="course-card" @click="openDetail(c)">
        <div class="course-thumb"><BookOpen :size="28" /></div>
        <div class="course-body">
          <p class="course-seq">课序 {{ c.seq }}</p><h4>{{ c.name }}</h4><p class="course-product">{{ c.product }}</p>
          <div class="course-meta"><Rating :modelValue="c.difficulty" readonly :cancel="false" /><span class="version-tag">{{ c.version }}</span></div>
          <div class="course-meta"><span class="spec-tag">{{ c.duration_spec || '未设置时间规格' }}</span><span class="price-tag">¥{{ formatPrice(c.unit_price) }}</span></div>
          <div v-if="getRelatedProperties(c)?.标题" class="related-summary">{{ getRelatedProperties(c).标题 }}</div>
          <div v-if="getCourseNames(c).length" class="course-list-inline">课程：{{ getCourseNames(c).join(' / ') }}</div>
        </div>
      </div>
    </div>
    <Dialog v-model:visible="showDetail" modal header="课程详情" :style="{width:'560px'}">
      <div v-if="activeCourse" class="detail-body">
        <h3>{{ activeCourse.name }}</h3><p class="muted">{{ activeCourse.product }} · 难度 <Rating :modelValue="activeCourse.difficulty" readonly :cancel="false" style="display:inline-flex" /></p>
        <div class="detail-grid">
          <div class="field"><label>时间规格</label><p>{{ activeCourse.duration_spec || '—' }}</p></div>
          <div class="field"><label>产品单价</label><p>¥{{ formatPrice(activeCourse.unit_price) }}</p></div>
        </div>
        <div v-if="getRelatedProperties(activeCourse)" class="field">
          <label>相关属性</label>
          <div class="related-card">
            <p class="related-heading">{{ getRelatedProperties(activeCourse).标题 || '价目表' }}</p>
            <p class="muted">{{ getRelatedProperties(activeCourse).课时说明 || '—' }}</p>
            <div v-for="category in getRelatedProperties(activeCourse).课程分类 || []" :key="category.分类" class="category-block">
              <div class="category-title">{{ category.分类 }}</div>
              <p class="muted">单价：{{ category.单价 }}</p>
              <p class="muted">课程：{{ (category.课程 || []).join(' / ') }}</p>
              <ul class="price-list">
                <li v-for="item in category.课时价格 || []" :key="`${category.分类}-${item.课时}`">{{ item.课时 }}课时 · ¥{{ item.价格 }}</li>
              </ul>
            </div>
          </div>
        </div>
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
        <div class="field"><label>时间规格</label><InputText v-model="form.duration_spec" placeholder="例如：45分钟/次" /></div>
        <div class="field"><label>产品单价</label><InputNumber v-model="form.unit_price" mode="currency" currency="CNY" locale="zh-CN" :min="0" /></div>
        <div class="field full"><label>课程信息</label><Textarea v-model="form.info" rows="3" autoResize /></div>
        <div class="field full"><label>课程目标</label><Textarea v-model="form.goal" rows="3" autoResize /></div>
        <div class="field full related-properties-editor">
          <div class="section-header">
            <label>相关属性</label>
            <Button label="新增分类" icon="pi pi-plus" text size="small" @click="addCategory" />
          </div>
          <div class="field">
            <label>机构</label>
            <InputText v-model="form.related_properties.机构" />
          </div>
          <div class="field">
            <label>标题</label>
            <InputText v-model="form.related_properties.标题" />
          </div>
          <div class="field full">
            <label>课时说明</label>
            <InputText v-model="form.related_properties.课时说明" />
          </div>
          <div v-for="(category, categoryIndex) in form.related_properties.课程分类" :key="`category-${categoryIndex}`" class="category-editor">
            <div class="section-subheader">
              <span>分类 {{ categoryIndex + 1 }}</span>
              <Button icon="pi pi-trash" text severity="danger" size="small" @click="removeCategory(categoryIndex)" />
            </div>
            <div class="form-grid inner-grid">
              <div class="field">
                <label>分类名称</label>
                <InputText v-model="category.分类" />
              </div>
              <div class="field">
                <label>单价</label>
                <InputText v-model="category.单价" />
              </div>
              <div class="field full">
                <label>课程名称</label>
                <div v-for="(courseName, courseIndex) in category.课程" :key="`course-${categoryIndex}-${courseIndex}`" class="inline-row">
                  <InputText v-model="category.课程[courseIndex]" />
                  <Button icon="pi pi-times" text severity="danger" size="small" @click="removeCourse(categoryIndex, courseIndex)" />
                </div>
                <Button label="新增课程" icon="pi pi-plus" text size="small" @click="addCourse(categoryIndex)" />
              </div>
              <div class="field full">
                <label>课时价格</label>
                <div v-for="(tier, tierIndex) in category.课时价格" :key="`tier-${categoryIndex}-${tierIndex}`" class="tier-row">
                  <InputNumber v-model="category.课时价格[tierIndex].课时" :min="1" placeholder="课时" />
                  <InputNumber v-model="category.课时价格[tierIndex].价格" :min="0" placeholder="价格" />
                  <Button icon="pi pi-times" text severity="danger" size="small" @click="removeTier(categoryIndex, tierIndex)" />
                </div>
                <Button label="新增价格档" icon="pi pi-plus" text size="small" @click="addTier(categoryIndex)" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </RecordDialog>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import { BookOpen } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import RecordDialog from '../../components/RecordDialog.vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Rating from 'primevue/rating'
import InputNumber from 'primevue/inputnumber'
import { useToast } from 'primevue/usetoast'
import { listCourseProducts, createCourseProduct, updateCourseProduct, deleteCourseProduct } from '../../api/school'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])
const loading = ref(false)

async function loadCourseProducts() {
  loading.value = true
  try {
    const data = await listCourseProducts()
    list.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadCourseProducts())
const showDetail = ref(false)
const activeCourse = ref(null)
function openDetail(c) { activeCourse.value = c; showDetail.value = true }
function editFromDetail() { showDetail.value = false; openEdit(activeCourse.value) }
const showEditor = ref(false)
const editing = ref(false)
function getRelatedProperties(course) {
  if (!course?.related_properties) return null
  if (typeof course.related_properties === 'string') {
    try { return JSON.parse(course.related_properties) } catch { return null }
  }
  return course.related_properties
}
function getCourseNames(course) {
  const relatedProperties = getRelatedProperties(course)
  if (!relatedProperties?.课程分类) return []
  return (relatedProperties.课程分类 || []).flatMap((category) => category.课程 || [])
}
function serializeRelatedProperties(value) {
  if (!value || !String(value).trim()) return null
  if (typeof value === 'string') {
    try { return JSON.parse(value) } catch (error) { throw new Error('相关属性必须是合法的 JSON') }
  }
  return value
}
function createDefaultRelatedProperties(courseName = '') {
  return {
    机构: '咔库编程中心',
    标题: '价目表',
    课时说明: '1课时=45分钟，1次课=2课时',
    课程分类: [
      {
        分类: courseName || '编程启蒙',
        单价: '75元/课时',
        课程: ['3-4岁小小工程师', '5岁扫卡编程'],
        课时价格: [
          { 课时: 30, 价格: 2250 },
          { 课时: 60, 价格: 4500 },
        ],
      },
    ],
  }
}
function cloneRelatedProperties(value) {
  if (!value) return createDefaultRelatedProperties()
  if (typeof value === 'string') {
    try { return JSON.parse(value) } catch { return createDefaultRelatedProperties() }
  }
  return JSON.parse(JSON.stringify(value))
}
function normalizeRelatedProperties(value) {
  const source = cloneRelatedProperties(value)
  return {
    机构: source?.机构 || '咔库编程中心',
    标题: source?.标题 || '价目表',
    课时说明: source?.课时说明 || '1课时=45分钟，1次课=2课时',
    课程分类: Array.isArray(source?.课程分类)
      ? source.课程分类.map((category) => ({
          分类: category?.分类 || '',
          单价: category?.单价 || '75元/课时',
          课程: Array.isArray(category?.课程) ? category.课程.filter(Boolean) : [],
          课时价格: Array.isArray(category?.课时价格)
            ? category.课时价格.map((tier) => ({ 课时: Number(tier?.课时 || 0), 价格: Number(tier?.价格 || 0) }))
            : [],
        }))
      : [],
  }
}
const form = ref({ name: '', product: '', difficulty: 3, version: 'v1.0', duration_spec: '', unit_price: 0, info: '', goal: '', related_properties: createDefaultRelatedProperties() })
watch(() => form.value.name, (newName) => {
  if (!newName) return
  const categories = form.value.related_properties?.课程分类
  if (Array.isArray(categories) && categories.length) {
    const firstCategory = categories[0]
    if (!firstCategory.分类 || ['编程启蒙', '编程基础', '编程进阶', '编程高阶', '算法编程'].includes(firstCategory.分类)) {
      firstCategory.分类 = newName
    }
  }
})
function openCreate() {
  editing.value = false
  form.value = {
    name: '',
    product: '',
    difficulty: 3,
    version: 'v1.0',
    duration_spec: '',
    unit_price: 0,
    info: '',
    goal: '',
    related_properties: createDefaultRelatedProperties(),
  }
  showEditor.value = true
}
function formatPrice(v) { return Number(v || 0).toFixed(2) }
function openEdit(row) {
  editing.value = true
  form.value = {
    ...row,
    related_properties: normalizeRelatedProperties(getRelatedProperties(row)),
  }
  showEditor.value = true
}
function addCategory() {
  form.value.related_properties.课程分类.push({
    分类: form.value.name || '',
    单价: '75元/课时',
    课程: [],
    课时价格: [{ 课时: 30, 价格: 2250 }],
  })
}
function removeCategory(index) {
  form.value.related_properties.课程分类.splice(index, 1)
}
function addCourse(categoryIndex) {
  form.value.related_properties.课程分类[categoryIndex].课程.push('')
}
function removeCourse(categoryIndex, courseIndex) {
  form.value.related_properties.课程分类[categoryIndex].课程.splice(courseIndex, 1)
}
function addTier(categoryIndex) {
  form.value.related_properties.课程分类[categoryIndex].课时价格.push({ 课时: 30, 价格: 0 })
}
function removeTier(categoryIndex, tierIndex) {
  form.value.related_properties.课程分类[categoryIndex].课时价格.splice(tierIndex, 1)
}
async function save() {
  try {
    const payload = { ...form.value }
    payload.related_properties = normalizeRelatedProperties(form.value.related_properties)
    if (editing.value) {
      await updateCourseProduct(payload.id, payload)
      toast.add({ severity: 'success', summary: '更新成功', life: 2500 })
    } else {
      await createCourseProduct(payload)
      toast.add({ severity: 'success', summary: '新增成功', life: 2500 })
    }
    await loadCourseProducts()
    showEditor.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: '保存失败', detail: e.message, life: 3000 })
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
.spec-tag { font-size: var(--text-xs); color: var(--color-text-muted); }
.price-tag { font-size: var(--text-sm); color: var(--color-primary); font-weight: 600; font-family: var(--font-mono); }
.related-summary { margin-top: var(--space-2); font-size: var(--text-xs); color: var(--color-primary); }
.course-list-inline { margin-top: var(--space-2); font-size: var(--text-xs); color: var(--color-text-muted); line-height: 1.5; }
.related-card { border: 1px solid var(--color-divider); border-radius: var(--radius-md); padding: var(--space-3); background: var(--color-surface-muted); display: flex; flex-direction: column; gap: var(--space-2); }
.related-heading { font-weight: 600; color: var(--color-text); }
.category-block { border-top: 1px solid var(--color-divider); padding-top: var(--space-2); }
.category-title { font-weight: 600; color: var(--color-text); }
.price-list { margin: 0; padding-left: var(--space-4); color: var(--color-text-muted); }
.detail-body { display: flex; flex-direction: column; gap: var(--space-3); }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); }
.detail-body h3 { font-size: var(--text-lg); }
.muted { color: var(--color-text-muted); font-size: var(--text-sm); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field label { font-size: var(--text-sm); color: var(--color-text-muted); font-weight: 500; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field.full { grid-column: 1 / -1; }
.related-properties-editor { padding: var(--space-3); border: 1px solid var(--color-divider); border-radius: var(--radius-md); background: var(--color-surface-muted); gap: var(--space-3); }
.section-header, .section-subheader { display: flex; align-items: center; justify-content: space-between; gap: var(--space-2); }
.section-subheader { font-size: var(--text-sm); color: var(--color-text-muted); }
.category-editor { border: 1px solid var(--color-divider); border-radius: var(--radius-md); padding: var(--space-3); background: var(--color-surface); display: flex; flex-direction: column; gap: var(--space-3); }
.inner-grid { gap: var(--space-3); }
.inline-row, .tier-row { display: flex; align-items: center; gap: var(--space-2); margin-top: var(--space-2); }
.inline-row > *, .tier-row > * { flex: 1; }
.inline-row :deep(.p-button), .tier-row :deep(.p-button) { flex: 0 0 auto; }
</style>
