<template>
  <Dialog
    v-model:visible="isVisible"
    :header="`文件预览: ${fileTitle}`"
    :modal="true"
    :maximizable="true"
    :style="{ width: '90vw', height: '85vh' }"
    @hide="handleClose"
    :breakpoints="{ '960px': '100vw' }"
  >
    <div class="document-viewer-container">
      <div v-if="showPptxToolbar" class="pptx-toolbar">
        <div class="pptx-toolbar-group">
          <Button
            icon="pi pi-angle-left"
            text
            rounded
            size="small"
            :disabled="currentSlideIndex <= 0"
            @click="goPrevSlide"
            v-tooltip="'上一页'"
          />
          <span class="pptx-slide-indicator">{{ currentSlideIndex + 1 }} / {{ slideCount }}</span>
          <Button
            icon="pi pi-angle-right"
            text
            rounded
            size="small"
            :disabled="currentSlideIndex >= slideCount - 1"
            @click="goNextSlide"
            v-tooltip="'下一页'"
          />
        </div>

        <div class="pptx-toolbar-group">
          <Button
            icon="pi pi-search-minus"
            text
            rounded
            size="small"
            :disabled="zoomPercent <= 10"
            @click="zoomOut"
            v-tooltip="'缩小'"
          />
          <span class="pptx-zoom-indicator">{{ zoomPercent }}%</span>
          <Button
            icon="pi pi-search-plus"
            text
            rounded
            size="small"
            :disabled="zoomPercent >= 400"
            @click="zoomIn"
            v-tooltip="'放大'"
          />
          <Button
            :label="fitMode === 'contain' ? '适应' : '原始'"
            text
            size="small"
            @click="toggleFitMode"
            class="pptx-fit-btn"
          />
        </div>
      </div>

      <!-- Document viewer -->
      <div ref="viewerContainer" class="viewer-wrapper"></div>

      <!-- Loading state -->
      <div v-if="isLoading" class="loading-state">
        <p>加载中...</p>
      </div>

      <!-- Error state -->
      <div v-if="!isLoading && error" class="error-state">
        <p>❌ 文件加载失败</p>
        <small>{{ error }}</small>
        <Button 
          label="重新尝试"
          icon="pi pi-refresh"
          text
          @click="retryLoad"
          class="mt-2"
        />
      </div>
      
      <!-- Fallback for unsupported types -->
      <div v-if="!isLoading && showFallback" class="fallback-container">
        <p>该文件类型暂不支持预览</p>
        <a :href="lastFileUrl" target="_blank" rel="noopener noreferrer">
          <Button label="在新标签页打开" icon="pi pi-external-link" />
        </a>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import { PptxViewer, RECOMMENDED_ZIP_LIMITS } from '@aiden0z/pptx-renderer';

const props = defineProps({
  visible: Boolean,
  fileUrl: String,
  fileName: String,
});

const emit = defineEmits(['update:visible']);

const isVisible = ref(props.visible);
const isLoading = ref(false);
const error = ref('');
const fileTitle = ref('');
const showFallback = ref(false);
const viewerContainer = ref(null);
const lastFileUrl = ref('');
const currentPreviewType = ref('');
const currentSlideIndex = ref(0);
const slideCount = ref(0);
const zoomPercent = ref(100);
const fitMode = ref('contain');
const showPptxToolbar = ref(false);
let viewer = null;

// Watch for visibility changes from parent
watch(() => props.visible, (newVal) => {
  isVisible.value = newVal;
  if (newVal && props.fileUrl) {
    // Dialog content mounts lazily; defer load until container ref is available.
    nextTick(() => {
      loadDocument(props.fileUrl);
    });
  }
});

// Watch for visibility changes from dialog itself
watch(isVisible, (newVal) => {
  emit('update:visible', newVal);
});

// Watch for file URL changes
watch(() => props.fileUrl, async (newUrl) => {
  if (newUrl) {
    await loadDocument(newUrl);
  }
});

// Update file title
watch(() => props.fileName, (newName) => {
  fileTitle.value = newName || '文件';
});

const getFileExtension = (url, fileName = '') => {
  const source = (fileName || url || '').toLowerCase();
  const lastDot = source.lastIndexOf('.');
  if (lastDot < 0 || lastDot === source.length - 1) return '';
  const rawExt = source.slice(lastDot + 1);
  const qIndex = rawExt.indexOf('?');
  return qIndex >= 0 ? rawExt.slice(0, qIndex) : rawExt;
};

const clearViewer = () => {
  if (viewer) {
    viewer.destroy?.();
    viewer = null;
  }
  if (viewerContainer.value) {
    viewerContainer.value.innerHTML = '';
  }
  currentPreviewType.value = '';
  showPptxToolbar.value = false;
  currentSlideIndex.value = 0;
  slideCount.value = 0;
  zoomPercent.value = 100;
  fitMode.value = 'contain';
};

const loadDocument = async (url) => {
  if (!viewerContainer.value) {
    await nextTick();
  }
  if (!viewerContainer.value) {
    throw new Error('预览容器尚未就绪，请重试');
  }

  isLoading.value = true;
  error.value = '';
  showFallback.value = false;
  lastFileUrl.value = url;
  currentPreviewType.value = '';
  clearViewer();

  try {
    const ext = getFileExtension(url, props.fileName);

    // Handle different file types
    if (['xlsx', 'xls'].includes(ext)) {
      loadExcelPreview(url);
    } else if (['docx', 'doc'].includes(ext)) {
      loadWordPreview(url);
    } else if (['pptx'].includes(ext)) {
      currentPreviewType.value = 'pptx';
      await loadPptxPreview(url);
    } else if (['ppt'].includes(ext)) {
      loadPptPreview(url);
    } else if (['pdf'].includes(ext)) {
      loadPdfPreview(url);
    } else if (['txt'].includes(ext)) {
      await loadTextPreview(url);
    } else {
      showFallback.value = true;
      error.value = `不支持的文件格式: .${ext}`;
    }

    isLoading.value = false;
  } catch (err) {
    console.error('Document loading error:', err);
    error.value = err.message || '无法加载此文件';
    isLoading.value = false;
  }
};

const loadExcelPreview = (url) => {
  // Embed Excel Online viewer
  const encodedUrl = encodeURIComponent(url);
  viewerContainer.value.innerHTML = `
    <iframe 
      src="https://view.officeapps.live.com/op/embed.aspx?src=${encodedUrl}"
      width="100%" 
      height="100%" 
      frameborder="0"
      style="border: none;"
    ></iframe>
  `;
};

const loadWordPreview = (url) => {
  // Embed Word Online viewer
  const encodedUrl = encodeURIComponent(url);
  viewerContainer.value.innerHTML = `
    <iframe 
      src="https://view.officeapps.live.com/op/embed.aspx?src=${encodedUrl}"
      width="100%" 
      height="100%" 
      frameborder="0"
      style="border: none;"
    ></iframe>
  `;
};

const loadPptPreview = (url) => {
  // Embed PowerPoint Online viewer
  const encodedUrl = encodeURIComponent(url);
  viewerContainer.value.innerHTML = `
    <iframe 
      src="https://view.officeapps.live.com/op/embed.aspx?src=${encodedUrl}"
      width="100%" 
      height="100%" 
      frameborder="0"
      style="border: none;"
    ></iframe>
  `;
};

const loadPptxPreview = async (url) => {
  // Render PPTX directly in browser; works for local blob URLs and remote files.
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('无法读取 PPTX 文件内容');
  }
  const buffer = await response.arrayBuffer();

  viewer = await PptxViewer.open(buffer, viewerContainer.value, {
    renderMode: 'slide',
    fitMode: fitMode.value,
    zoomPercent: zoomPercent.value,
    zipLimits: RECOMMENDED_ZIP_LIMITS,
    lazySlides: true,
    lazyMedia: true,
  });

  slideCount.value = viewer.slideCount || 0;
  currentSlideIndex.value = 0;
  showPptxToolbar.value = slideCount.value > 0;

  viewer.on('slidechange', (event) => {
    currentSlideIndex.value = event.detail.index;
  });
};

const goPrevSlide = async () => {
  if (!viewer || currentSlideIndex.value <= 0) return;
  await viewer.goToSlide(currentSlideIndex.value - 1);
};

const goNextSlide = async () => {
  if (!viewer || currentSlideIndex.value >= slideCount.value - 1) return;
  await viewer.goToSlide(currentSlideIndex.value + 1);
};

const zoomOut = async () => {
  if (!viewer) return;
  const next = Math.max(10, zoomPercent.value - 10);
  zoomPercent.value = next;
  await viewer.setZoom(next);
};

const zoomIn = async () => {
  if (!viewer) return;
  const next = Math.min(400, zoomPercent.value + 10);
  zoomPercent.value = next;
  await viewer.setZoom(next);
};

const toggleFitMode = async () => {
  if (!viewer) return;
  fitMode.value = fitMode.value === 'contain' ? 'none' : 'contain';
  await viewer.setFitMode(fitMode.value);
};

const loadPdfPreview = (url) => {
  // Embed PDF viewer
  viewerContainer.value.innerHTML = `
    <iframe 
      src="${url}"
      width="100%" 
      height="100%" 
      frameborder="0"
      style="border: none;"
    ></iframe>
  `;
};

const loadTextPreview = async (url) => {
  // Fetch and display text content
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch');
    const text = await response.text();
    viewerContainer.value.innerHTML = `
      <pre style="padding: 16px; overflow: auto; font-size: 13px; line-height: 1.5; font-family: 'Monaco', 'Menlo', monospace;">${escapeHtml(text)}</pre>
    `;
  } catch (err) {
    throw new Error('Unable to load text file');
  }
};

const escapeHtml = (text) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
};

const retryLoad = () => {
  if (lastFileUrl.value) {
    loadDocument(lastFileUrl.value);
  }
};

const handleClose = () => {
  // Cleanup viewer
  clearViewer();
  error.value = '';
  showFallback.value = false;
  emit('update:visible', false);
};

onMounted(() => {
  // Load document if props already set
  if (props.fileUrl) {
    loadDocument(props.fileUrl);
  }
});
</script>

<style scoped>
.document-viewer-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.viewer-wrapper {
  flex: 1;
  overflow: auto;
  background: white;
}

.pptx-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  flex-wrap: wrap;
}

.pptx-toolbar-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pptx-slide-indicator,
.pptx-zoom-indicator {
  font-size: 12px;
  color: #334155;
  min-width: 64px;
  text-align: center;
}

.pptx-fit-btn {
  min-width: 52px;
}

.loading-state,
.error-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: auto;
  padding: 2rem;
  text-align: center;
  color: #666;
  background: rgba(245, 245, 245, 0.96);
  z-index: 2;
}

.loading-state p,
.error-state p {
  font-size: 16px;
  margin-bottom: 0.5rem;
}

.error-state small {
  color: #999;
  font-size: 12px;
}

.fallback-container {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: auto;
  gap: 1rem;
  padding: 2rem;
  color: #666;
  background: rgba(245, 245, 245, 0.96);
  z-index: 2;
}

.mt-2 {
  margin-top: 0.5rem;
}
</style>
