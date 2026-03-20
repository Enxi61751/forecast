<template>
  <div v-if="modelValue && selected" class="mask" @click.self="$emit('update:modelValue', false)">
    <section class="card modal">
      <header class="modal-head">
        <h3>{{ selected.name }}详情</h3>
        <button class="close" type="button" @click="$emit('update:modelValue', false)">关闭</button>
      </header>

      <div class="range-switch">
        <button
          v-for="option in options"
          :key="option"
          class="range-btn"
          :class="{ active: option === range }"
          type="button"
          @click="$emit('update:range', option)"
        >
          {{ option }}
        </button>
      </div>

      <ChartPanel title="原油价格趋势" :labels="selected.labels[range]" :values="selected.trend[range]" :height="280" :enable-zoom="true" />
    </section>
  </div>
</template>

<script setup lang="ts">
import ChartPanel from "@/components/common/ChartPanel.vue";
import type { ExchangeRateCardData, ExchangeTimeRange } from "@/types/exchange";

defineProps<{
  modelValue: boolean;
  selected: ExchangeRateCardData | null;
  range: ExchangeTimeRange;
}>();

const options: ExchangeTimeRange[] = ["1W", "1M", "6M"];

defineEmits<{
  "update:modelValue": [value: boolean];
  "update:range": [value: ExchangeTimeRange];
}>();
</script>

<style scoped>
.mask {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 14, 0.64);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 40;
}

.modal {
  width: min(900px, 100%);
  padding: 16px;
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.modal-head h3 {
  margin: 0;
}

.close {
  border: 1px solid rgba(120, 155, 255, 0.6);
  background: rgba(79, 130, 255, 0.16);
  color: var(--color-text-primary);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  cursor: pointer;
}

.range-switch {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.range-btn {
  border: 1px solid rgba(136, 163, 255, 0.45);
  border-radius: 8px;
  background: rgba(13, 20, 40, 0.85);
  color: var(--color-text-secondary);
  padding: 7px 10px;
  cursor: pointer;
}

.range-btn.active {
  color: var(--color-text-primary);
  background: rgba(79, 130, 255, 0.25);
}
</style>
