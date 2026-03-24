<template>
  <section class="card report-card">
    <header class="report-head">
      <h3>{{ title }}</h3>
      <button class="download-btn" type="button" :disabled="!canDownload" @click="$emit('download')">
        下载报告
      </button>
    </header>
    <div class="report-content">
      <p v-if="content">{{ content }}</p>
      <p v-else class="placeholder">暂未生成内容，请先运行预测或等待接口可用。</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  content: string;
  canDownload: boolean;
}>();

defineEmits<{
  download: [];
}>();
</script>

<style scoped>
.report-card {
  padding: 16px;
}

.report-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.report-head h3 {
  margin: 0;
  font-size: 16px;
}

.download-btn {
  border: 1px solid rgba(110, 145, 255, 0.72);
  border-radius: var(--radius-sm);
  background: rgba(79, 130, 255, 0.16);
  color: var(--color-text-primary);
  padding: 8px 12px;
  cursor: pointer;
}

.download-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.report-content {
  border-radius: var(--radius-md);
  border: 1px solid rgba(118, 153, 255, 0.22);
  background: rgba(8, 12, 28, 0.75);
  padding: 12px;
  color: var(--color-text-secondary);
  white-space: pre-line;
  min-height: 140px;
}

.report-content p {
  margin: 0;
  line-height: 1.62;
}

.placeholder {
  color: var(--color-text-muted);
}
</style>
