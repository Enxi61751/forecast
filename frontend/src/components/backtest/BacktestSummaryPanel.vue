<template>
  <section class="card summary-panel">
    <header class="summary-head">
      <div>
        <p class="eyebrow">Backtest Summary</p>
        <h3>{{ strategyName || "Strategy pending" }}</h3>
      </div>
      <div class="head-right">
        <div class="summary-meta">
          <span>Benchmark: {{ benchmarkName || "Unavailable" }}</span>
          <span>Period: {{ periodLabel || "Unavailable" }}</span>
        </div>
        <div class="head-actions">
          <button class="action-btn" :class="{ active: showComparison }" @click="toggleComparison">
            模拟交易
          </button>
          <button class="action-btn" @click="handleExport">
            导出
          </button>
        </div>
      </div>
    </header>
    <div class="summary-grid">
      <article class="summary-block">
        <h4>Trade Summary</h4>
        <p>{{ tradeSummary || "当前分支尚未返回 trade summary。" }}</p>
      </article>
      <article class="summary-block">
        <h4>Period Summary</h4>
        <p>{{ periodSummary || "当前分支尚未返回 period summary。" }}</p>
      </article>
      <article class="summary-block">
        <h4>Notes</h4>
        <p>{{ notes || "可在后端接口合并后补充策略说明和附加解释。" }}</p>
      </article>
    </div>
    <StrategyComparisonTable v-if="showComparison" :rows="comparisonData" />
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import StrategyComparisonTable from "./StrategyComparisonTable.vue";
import { mockStrategyComparison } from "@/mocks/backtest";

defineProps<{
  strategyName: string | null;
  benchmarkName: string | null;
  periodLabel: string | null;
  notes: string | null;
  tradeSummary: string | null;
  periodSummary: string | null;
}>();

const showComparison = ref(true);
const comparisonData = mockStrategyComparison;

function toggleComparison(): void {
  showComparison.value = !showComparison.value;
}

function handleExport(): void {
  // TODO: implement export functionality
  console.log("export clicked");
}
</script>

<style scoped>
.summary-panel {
  padding: 1.5rem;
}

.summary-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.summary-head .eyebrow {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.summary-head h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.head-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
}

.summary-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.head-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  background: rgba(79, 130, 255, 0.08);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background: rgba(79, 130, 255, 0.18);
}

.action-btn.active {
  background: var(--color-accent);
  color: #fff;
  border-color: var(--color-accent);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-block h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.summary-block p {
  font-size: 0.875rem;
  color: var(--color-text-primary);
  line-height: 1.5;
}

.summary-block {
  border-radius: var(--radius-md);
  border: 1px solid rgba(132, 161, 255, 0.18);
  background: rgba(7, 13, 30, 0.62);
  padding: 12px;
}

@media (max-width: 980px) {
  .head-right {
    width: 100%;
    align-items: flex-start;
  }

  .summary-meta {
    flex-direction: column;
    gap: 0.4rem;
  }
}

@media (max-width: 640px) {
  .head-actions {
    width: 100%;
  }

  .action-btn {
    flex: 1;
  }
}
</style>
