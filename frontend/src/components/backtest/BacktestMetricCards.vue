<template>
  <section class="metric-grid">
    <article v-for="metric in metrics" :key="metric.id" class="card metric-card" :class="metric.tone || 'neutral'">
      <p>{{ metric.label }}</p>
      <h3>{{ metric.value }}</h3>
    </article>
  </section>
</template>

<script setup lang="ts">
import type { BacktestMetricItem } from "@/types/backtest";

defineProps<{
  metrics: BacktestMetricItem[];
}>();
</script>

<style scoped>
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 14px;
}

.metric-card p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.metric-card h3 {
  margin: 8px 0 0;
  font-size: 20px;
}

.metric-card.positive {
  border-color: rgba(30, 201, 143, 0.35);
}

.metric-card.negative {
  border-color: rgba(255, 90, 133, 0.35);
}

@media (max-width: 980px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
