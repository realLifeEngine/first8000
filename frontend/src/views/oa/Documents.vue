<template>
  <div>
    <PageHeader title="文件柜" crumb="办公OA > 文件柜" subtitle="合同、制度与模板文档统一管理">
      <template #actions><Button label="上传文档" icon="pi pi-upload" @click="upload" /></template>
    </PageHeader>
    <div class="table-card">
      <DataTable :value="list" paginator :rows="10" dataKey="id" responsiveLayout="scroll" stripedRows removableSort>
        <Column field="category" header="分类" sortable />
        <Column header="文档标题" field="title" sortable><template #body="{ data }"><div class="title-cell"><Star v-if="data.starred" :size="14" class="star" /><FileText :size="15" class="file-icon" /><span>{{ data.title }}</span></div></template></Column>
        <Column field="publisher" header="上传人" sortable /><Column field="createTime" header="上传时间" sortable /><Column field="editTime" header="最近编辑" sortable />
        <Column header="操作" style="width:100px"><template #body="{ data }"><Button label="下载" size="small" text @click="download(data)" /></template></Column>
      </DataTable>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { Star, FileText } from 'lucide-vue-next'
import PageHeader from '../../components/PageHeader.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
import { documents } from '../../api/oa'
import { useAuthStore } from '../../stores/auth'
const toast = useToast()
const auth = useAuthStore()
const list = ref([])
const loading = ref(false)

async function loadDocuments() {
  loading.value = true
  try {
    const data = await documents.list()
    list.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: '加载失败', detail: e.message, life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => loadDocuments())

function upload() { toast.add({ severity: 'info', summary: '演示环境', detail: '文档上传功能在演示环境中不可用', life: 2500 }) }
function download(row) { toast.add({ severity: 'success', summary: '下载中', detail: `正在下载「${row.title}」`, life: 2500 }) }
</script>
<style scoped>
.table-card { background: var(--color-surface); border: 1px solid var(--color-divider); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-sm); }
.title-cell { display: flex; align-items: center; gap: var(--space-2); }
.star { color: var(--color-warning); flex-shrink: 0; }
.file-icon { color: var(--color-text-faint); flex-shrink: 0; }
</style>
