<template>
  <section class="card summary-panel">
    <header class="summary-head">
      <div>
        <p class="eyebrow">Backtest Summary</p>
        <h3>{{ strategyName || "Strategy pending" }}</h3>
      </div>
      <div class="summary-meta">
        <span>Benchmark: {{ benchmarkName || "Unavailable" }}</span>
        <span>Period: {{ periodLabel || "Unavailable" }}</span>
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
  </section>
</template>

<script setup lang="ts">
defineProps<{
  strategyName: string | null;
  benchmarkName: string | null;
  periodLabel: string | null;
  notes: string | null;
  tradeSummary: string | null;
  periodSummary: string | null;
}>();
</script>

<style scoped>
.summary-panel {
  padding: 16px;
  display: grid;
  gap: 16px;
}

.summary-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--color-text-secondary);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.summary-head h3,
.summary-block h4 {
  margin: 0;
}

.summary-meta {
  display: grid;
  gap: 6px;
  color: var(--color-text-secondary);
  font-size: 13px;
  text-align: right;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-block {
  border-radius: var(--radius-md);
  border: 1px solid rgba(132, 161, 255, 0.18);
  background: rgba(7, 13, 30, 0.62);
  padding: 12px;
}

.summary-block p {
  margin: 8px 0 0;
  color: var(--color-text-secondary);
  line-height: 1.65;
}

@media (max-width: 980px) {
  .summary-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-meta {
    text-align: left;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
