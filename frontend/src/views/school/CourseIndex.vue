<template>
  <div class="course-index-page">
    <PageHeader title="查阅课程" crumb="教务管理 > 查阅课程" subtitle="浏览课程目录与资源索引">
      <template #actions>
        <Button label="刷新列表" icon="pi pi-refresh" outlined size="small" @click="reloadProducts" />
      </template>
    </PageHeader>

    <div class="course-index-shell">
      <aside class="ci-sidebar">
        <div class="ci-sidebar-header">
          <div>
            <div class="ci-sidebar-title">课程目录</div>
            <div class="ci-sidebar-subtitle">{{ products.length }} 个课程产品</div>
          </div>
          <span class="ci-total">{{ products.length }}</span>
        </div>
        <div class="ci-search-wrap">
          <InputText v-model="productSearch" placeholder="搜索课程名称或产品" size="small" class="ci-search" />
        </div>
        <ul class="ci-product-list">
          <li
            v-for="p in filteredProducts"
            :key="p.id"
            class="ci-product-item"
            :class="{ active: selectedProduct && selectedProduct.id === p.id }"
            @click="selectProduct(p)"
          >
            <div class="ci-product-icon ci-product-icon-ready">
              <FolderOpen :size="14" />
            </div>
            <div class="ci-product-copy">
              <span class="ci-product-name" :title="p.name">{{ p.name }}</span>
            </div>
          </li>
        </ul>
      </aside>

      <div class="ci-browser">
        <div v-if="!selectedProduct" class="ci-empty">
          <div class="ci-empty-card">
            <FolderOpen :size="48" class="ci-empty-icon" />
            <h3>选择一门课程开始浏览</h3>
            <p>可查看当前课程目录下的文件与资源内容。</p>
            <Button label="重新加载课程" icon="pi pi-refresh" @click="reloadProducts" />
          </div>
        </div>

        <template v-else>
          <div class="ci-detail-card">
            <div class="ci-detail-top">
              <div class="ci-detail-copy">
                <div class="ci-detail-title">{{ selectedProduct.name }}</div>
                <div class="ci-detail-meta">课程目录与资源清单</div>
              </div>
              <div class="ci-detail-actions">
                <Button label="刷新目录" icon="pi pi-refresh" text size="small" @click="reloadSelectedProduct" />
              </div>
            </div>
            <div class="ci-pill-row">
              <Tag v-if="selectedProduct.in_index" value="有本地索引" severity="success" />
              <Tag v-else value="仅数据库" severity="secondary" />
            </div>
          </div>

          <div class="ci-content-card">
            <div class="ci-breadcrumb-bar" v-if="selectedProduct.in_index">
              <div class="ci-toolbar">
                <span class="ci-count">{{ filteredItems.length }} 项</span>
                <InputText v-model="fileSearch" placeholder="过滤文件名…" size="small" class="ci-file-search" />
              </div>
            </div>

            <div class="ci-table-scroll">
              <DataTable
                v-if="selectedProduct.in_index"
                :value="filteredItems"
                :loading="loading"
                size="small"
                stripedRows
                class="ci-table"
              >
                <Column header="类型" style="width: 48px; text-align: center">
                  <template #body="{ data }">
                    <Folder v-if="data.is_dir" :size="15" class="icon-dir" />
                    <File v-else :size="15" class="icon-file" />
                  </template>
                </Column>

                <Column field="name" header="名称">
                  <template #body="{ data }">
                    <span class="ci-indent" :style="{ paddingLeft: Math.max(0, data.depth - 1) * 18 + 'px' }">
                      <a v-if="!data.is_dir" :href="data.url" target="_blank" rel="noopener noreferrer" class="ci-file-link">{{ data.name }}</a>
                      <span v-else class="ci-dir-name">{{ data.name }}/</span>
                    </span>
                  </template>
                </Column>

                <Column field="path" header="路径" class="ci-path-col">
                  <template #body="{ data }">
                    <span class="ci-path-text" :title="data.path">{{ data.path }}</span>
                  </template>
                </Column>

                <Column header="层级" style="width: 64px; text-align: center">
                  <template #body="{ data }">
                    <Tag :value="`L${data.depth}`" severity="secondary" />
                  </template>
                </Column>

                <Column header="下载" style="width: 84px; text-align: center">
                  <template #body="{ data }">
                    <a v-if="!data.is_dir && data.url" :href="data.url" target="_blank" rel="noopener noreferrer" download>
                      <Button class="ci-download-btn" icon="pi pi-download" text rounded size="small" v-tooltip="'下载文件'" />
                    </a>
                  </template>
                </Column>
              </DataTable>
            </div>

            <div class="ci-pagination" v-if="selectedProduct.in_index && totalPages > 1">
              <button
                class="ci-page-nav"
                :disabled="currentPage === 1"
                @click="goToPage(currentPage - 1)"
              >
                <span class="pi pi-angle-left"></span>
                <span>上一页</span>
              </button>

              <div class="ci-page-dots">
                <template v-for="page in pageButtons" :key="page">
                  <button
                    v-if="page !== 'ellipsis'"
                    class="ci-page-number"
                    :class="{ active: page === currentPage }"
                    @click="goToPage(page)"
                  >
                    {{ page }}
                  </button>
                  <span v-else class="ci-page-ellipsis">…</span>
                </template>
              </div>

              <button
                class="ci-page-nav"
                :disabled="currentPage >= totalPages"
                @click="goToPage(currentPage + 1)"
              >
                <span>下一页</span>
                <span class="pi pi-angle-right"></span>
              </button>
            </div>
            <div class="ci-pagination-summary" v-if="selectedProduct.in_index">
              第 {{ currentPage }} / {{ totalPages }} 页 · 共 {{ totalItems }} 条
            </div>
            <div v-if="!selectedProduct.in_index" class="ci-no-index">
              <span>此课程在本地服务器无索引，无法浏览文件目录</span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FolderOpen, Folder, File } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { listCourseIndexProducts, getCourseIndex } from '../../api/school'
import { createRequestGuard, scrollToTop } from './courseIndexPagination'

const toast = useToast()
const requestGuard = createRequestGuard()
const products = ref([])
const productSearch = ref('')
const selectedProduct = ref(null)
const allItems = ref([])
const loading = ref(false)
const fileSearch = ref('')
const currentPage = ref(1)
const totalItems = ref(0)
const PAGE_SIZE = 80

const filteredProducts = computed(() => {
  const q = productSearch.value.trim().toLowerCase()
  if (!q) return products.value
  return products.value.filter((p) => p.name.toLowerCase().includes(q) || (p.product || '').toLowerCase().includes(q))
})

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / PAGE_SIZE)))

const pageButtons = computed(() => {
  const total = totalPages.value
  if (total <= 1) return [1]

  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(total, start + 4)
  for (let page = start; page <= end; page += 1) {
    pages.push(page)
  }
  if (start > 1) pages.unshift('ellipsis')
  if (end < total) pages.push('ellipsis')
  return pages
})

const filteredItems = computed(() => {
  let list = allItems.value
  const q = fileSearch.value.trim().toLowerCase()
  if (q) {
    list = list.filter((i) => i.name.toLowerCase().includes(q) || i.path.toLowerCase().includes(q))
  }
  return list
})

async function loadProducts() {
  try {
    const data = await listCourseIndexProducts()
    products.value = data
    if (!selectedProduct.value && data.length) {
      const firstProduct = data[0]
      selectedProduct.value = firstProduct
      await selectProduct(firstProduct, true)
    } else if (selectedProduct.value) {
      const current = data.find((item) => item.id === selectedProduct.value.id)
      if (current) {
        await selectProduct(current, true)
      } else {
        selectedProduct.value = null
        allItems.value = []
      }
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: '无法获取课程列表', life: 3000 })
  }
}

async function loadIndexPage(productName, page = 1) {
  if (!productName) return
  const requestToken = requestGuard.beginRequest()
  loading.value = true

  try {
    const data = await getCourseIndex(productName, { page, page_size: PAGE_SIZE })
    if (!requestGuard.isCurrent(requestToken)) return
    if (selectedProduct.value?.name !== productName) return

    allItems.value = data.items || []
    totalItems.value = data.total ?? 0
    currentPage.value = page
  } catch (e) {
    if (!requestGuard.isCurrent(requestToken)) return
    toast.add({ severity: 'error', summary: '加载失败', detail: `无法获取 ${productName} 的文件列表`, life: 3000 })
    allItems.value = []
    totalItems.value = 0
    currentPage.value = 1
  } finally {
    if (requestGuard.isCurrent(requestToken)) {
      loading.value = false
    }
  }
}

async function selectProduct(p, force = false) {
  if (selectedProduct.value?.id === p.id && !force) return
  requestGuard.invalidate()
  selectedProduct.value = p
  fileSearch.value = ''
  allItems.value = []
  totalItems.value = 0
  currentPage.value = 1
  if (!p.in_index) {
    loading.value = false
    return
  }
  await loadIndexPage(p.name, 1)
}

function goToPage(page) {
  if (!selectedProduct.value?.name) return
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  scrollToTop()
  loadIndexPage(selectedProduct.value.name, page)
}

async function reloadSelectedProduct() {
  if (!selectedProduct.value) return
  await selectProduct(selectedProduct.value, true)
}

async function reloadProducts() {
  await loadProducts()
}

onMounted(loadProducts)
</script>

<style scoped>
.course-index-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  width: 100%;
}
.course-index-shell {
  display: flex;
  min-height: calc(100vh - 180px);
  overflow: hidden;
  border: 1px solid var(--color-divider, #e2e8f0);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
  width: 100%;
}
.ci-sidebar {
  width: 280px;
  min-width: 240px;
  flex-shrink: 0;
  border-right: 1px solid var(--color-divider, #e2e8f0);
  display: flex;
  flex-direction: column;
  background: var(--color-surface-offset);
}
.ci-sidebar-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-divider, #e2e8f0);
}
.ci-sidebar-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}
.ci-sidebar-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
}
.ci-total {
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-full);
  padding: 2px 8px;
  font-size: var(--text-xs);
  font-weight: 600;
}
.ci-search-wrap {
  padding: var(--space-3) var(--space-4) var(--space-2);
}
.ci-search { width: 100%; }
.ci-product-list {
  list-style: none;
  margin: 0;
  padding: var(--space-2) var(--space-3) var(--space-4);
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.ci-product-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-3);
  cursor: pointer;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background: transparent;
  transition: all 0.15s ease;
}
.ci-product-item:hover {
  background: var(--color-surface);
  border-color: var(--color-divider);
}
.ci-product-item.active {
  background: var(--color-surface);
  border-color: var(--color-primary);
  box-shadow: inset 2px 0 0 var(--color-primary);
}
.ci-product-icon {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: var(--color-surface-offset);
  color: var(--color-text-muted);
  flex-shrink: 0;
}
.ci-product-icon-ready {
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-success);
}
.ci-product-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}
.ci-product-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ci-product-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ci-status-tag { margin-left: auto; flex-shrink: 0; }

.ci-browser {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: var(--space-4);
  gap: var(--space-4);
  background: linear-gradient(180deg, rgba(255,255,255,0.6), rgba(248,250,252,0.8));
}
.ci-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ci-empty-card {
  width: min(420px, 100%);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-3);
}
.ci-empty-icon { color: var(--color-primary); }
.ci-empty-card h3 { margin: 0; font-size: var(--text-lg); color: var(--color-text); }
.ci-empty-card p { margin: 0; font-size: var(--text-sm); color: var(--color-text-muted); line-height: 1.6; }

.ci-detail-card,
.ci-related-card,
.ci-content-card {
  background: var(--color-surface);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}
.ci-detail-card { padding: var(--space-4); display: flex; flex-direction: column; gap: var(--space-3); }
.ci-detail-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}
.ci-detail-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ci-detail-meta {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-top: 4px;
}
.ci-detail-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}
.ci-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
.ci-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-4) var(--space-3);
  border-bottom: 1px solid var(--color-divider);
}
.ci-card-head h3 { margin: 0; font-size: var(--text-base); font-weight: 600; color: var(--color-text); }
.ci-card-head span { font-size: var(--text-sm); color: var(--color-text-muted); }
.ci-related-card { overflow: hidden; }
.ci-category-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4) var(--space-4);
}
.ci-category-item {
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: var(--color-surface-offset);
}
.ci-category-title {
  font-weight: 600;
  color: var(--color-text);
}
.ci-category-meta {
  margin-top: 4px;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
.ci-price-list {
  margin: 8px 0 0 18px;
  padding: 0;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
.ci-content-card { overflow: hidden; display: flex; flex-direction: column; min-height: 0; }
.ci-breadcrumb-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-divider);
  background: var(--color-surface-offset);
  gap: var(--space-3);
  flex-wrap: wrap;
}
.ci-breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
.ci-bc-root { font-family: monospace; font-size: var(--text-xs); }
.ci-bc-current { font-weight: 600; color: var(--color-text); max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ci-toolbar { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.ci-count { font-size: var(--text-sm); color: var(--color-text-muted); }
.ci-depth-select { width: 130px; }
.ci-file-search { width: 180px; }
.ci-table-scroll {
  flex: 1;
  overflow: auto;
  min-height: 0;
}
.ci-table { width: 100%; }
.ci-loading-more {
  padding: var(--space-3) var(--space-4);
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
.ci-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  padding: var(--space-3) var(--space-4) 0;
}
.ci-pagination-summary {
  padding: 0 var(--space-4) var(--space-4);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}
.ci-page-dots {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.ci-page-nav,
.ci-page-number {
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text);
  border-radius: 999px;
  height: 32px;
  min-width: 32px;
  padding: 0 10px;
  font-size: var(--text-sm);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.16s ease;
}
.ci-page-nav:hover:not(:disabled),
.ci-page-number:hover:not(.active) {
  background: var(--color-surface-offset);
  border-color: var(--color-divider);
}
.ci-page-nav:disabled {
  color: var(--color-text-faint);
  cursor: not-allowed;
  opacity: 0.6;
}
.ci-page-number.active {
  background: var(--color-primary);
  color: #fff;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
}
.ci-page-ellipsis {
  padding: 0 2px;
  color: var(--color-text-muted);
  font-size: var(--text-base);
}
.icon-dir { color: #f59e0b; }
.icon-file { color: #94a3b8; }
.ci-indent { display: inline-block; }
.ci-file-link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: var(--text-sm);
}
.ci-file-link:hover { text-decoration: underline; }
.ci-download-btn {
  color: var(--color-primary);
  border: 1px solid var(--color-divider);
  background: var(--color-surface);
}
.ci-download-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-highlight);
  border-color: var(--color-primary);
}
.ci-download-btn:hover :deep(.p-button-icon) {
  color: #fff;
}
.ci-download-btn :deep(.p-button-icon) {
  color: inherit;
}
.ci-dir-name { font-weight: 600; font-size: var(--text-sm); color: var(--color-text); }
.ci-path-col { max-width: 320px; }
.ci-path-text {
  font-size: var(--text-xs);
  font-family: monospace;
  color: var(--color-text-muted);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ci-no-index {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  padding: var(--space-6);
}

@media (max-width: 980px) {
  .course-index-shell { flex-direction: column; }
  .ci-sidebar { width: auto; min-width: 0; border-right: 0; border-bottom: 1px solid var(--color-divider); max-height: 320px; }
  .ci-browser { padding: var(--space-3); }
  .ci-detail-top { flex-direction: column; }
}
</style>
