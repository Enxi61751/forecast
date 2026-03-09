<template>
  <section class="card status-card">
    <header class="status-head">
      <h3>运行状态</h3>
      <p>{{ message }}</p>
    </header>

    <div class="status-grid">
      <article class="step" :class="{ active: phase === 'idle' }">
        <span>未开始</span>
      </article>
      <article class="step" :class="{ active: phase === 'running' }">
        <span>运行中</span>
      </article>
      <article class="step" :class="{ active: phase === 'success' }">
        <span>已完成</span>
      </article>
      <article class="step" :class="{ active: phase === 'error' }">
        <span>失败</span>
      </article>
    </div>

    <div class="progress-wrap">
      <div class="progress-bar">
        <i :style="{ width: `${progress}%` }" />
      </div>
      <div class="meta-row">
        <span>进度 {{ progress }}%</span>
        <span>{{ runIdText }}</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { RunPhase } from "@/types/predict";

const props = defineProps<{
  phase: RunPhase;
  progress: number;
  message: string;
  runId: string | null;
}>();

const runIdText = computed(() => (props.runId ? `Run ID: ${props.runId}` : "Run ID: -"));
</script>

<style scoped>
.status-card {
  padding: 16px;
}

.status-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.status-head h3 {
  margin: 0;
  font-size: 16px;
}

.status-head p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.step {
  border: 1px solid rgba(125, 156, 255, 0.28);
  border-radius: 10px;
  background: rgba(9, 14, 30, 0.7);
  color: var(--color-text-muted);
  text-align: center;
  padding: 9px 6px;
  font-size: 12px;
}

.step.active {
  color: #dbe8ff;
  border-color: rgba(122, 161, 255, 0.66);
  background: rgba(79, 130, 255, 0.24);
}

.progress-wrap {
  margin-top: 12px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(22, 34, 71, 0.9);
  overflow: hidden;
}

.progress-bar i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #4f82ff, #6a5eff);
  transition: width 0.2s ease;
}

.meta-row {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: var(--color-text-secondary);
  font-size: 12px;
}

@media (max-width: 720px) {
  .status-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
