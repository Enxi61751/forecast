<template>
  <section class="summary-grid">
    <article class="card summary-card">
      <p>趋势判断</p>
      <h3>{{ trend || "--" }}</h3>
    </article>
    <article class="card summary-card">
      <p>风险提示</p>
      <h3>{{ risk || "Unavailable" }}</h3>
    </article>
    <article class="card summary-card">
      <p>置信度</p>
      <h3>{{ confidenceText }}</h3>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  trend: string;
  risk: string | null;
  confidence: number | null;
}>();

const confidenceText = computed(() => (
  typeof props.confidence === "number" ? `${(props.confidence * 100).toFixed(1)}%` : "Unavailable"
));
</script>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  padding: 14px;
}

.summary-card p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.summary-card h3 {
  margin: 8px 0 0;
  font-size: 18px;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
