<template>
  <div v-if="status === 'loading'" class="state-box loading">
    <div class="pulse" />
    <p>{{ loadingText }}</p>
  </div>
  <div v-else-if="status === 'empty'" class="state-box empty">
    <p>{{ emptyText }}</p>
  </div>
  <div v-else-if="status === 'error'" class="state-box error">
    <p>{{ errorText }}</p>
    <button v-if="showRetry" class="retry-btn" type="button" @click="$emit('retry')">重试</button>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { LoadStatus } from "@/types/common";

const props = withDefaults(
  defineProps<{
    status: LoadStatus;
    loadingText?: string;
    emptyText?: string;
    errorMessage?: string;
    showRetry?: boolean;
  }>(),
  {
    loadingText: "加载中...",
    emptyText: "暂无数据",
    errorMessage: "加载失败，请稍后重试",
    showRetry: false
  }
);

defineEmits<{
  retry: [];
}>();

const errorText = computed(() => props.errorMessage || "加载失败，请稍后重试");
</script>

<style scoped>
.state-box {
  min-height: 180px;
  border: 1px dashed rgba(118, 155, 255, 0.42);
  border-radius: var(--radius-md);
  background: rgba(14, 23, 52, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--color-text-secondary);
}

.pulse {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid rgba(118, 155, 255, 0.2);
  border-top-color: var(--color-accent);
  animation: spin 0.9s linear infinite;
}

.retry-btn {
  border: 1px solid rgba(118, 155, 255, 0.6);
  border-radius: 10px;
  padding: 8px 14px;
  color: var(--color-text-primary);
  background: rgba(79, 130, 255, 0.16);
  cursor: pointer;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
