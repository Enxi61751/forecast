<template>
  <button class="card rate-card" type="button" @click="$emit('open', data)">
    <div class="top-row">
      <h3>{{ data.pair }}</h3>
      <span :class="['change', data.change >= 0 ? 'up' : 'down']">
        {{ data.change >= 0 ? '+' : '' }}{{ data.change.toFixed(2) }}%
      </span>
    </div>
    <p class="name">{{ data.name }}</p>
    <p class="price">{{ data.price.toFixed(4) }}</p>
    <div class="meta">
      <span>高 {{ data.high.toFixed(4) }}</span>
      <span>低 {{ data.low.toFixed(4) }}</span>
    </div>
    <p class="time">{{ data.updatedAt }}</p>
  </button>
</template>

<script setup lang="ts">
import type { ExchangeRateCardData } from "@/types/exchange";

defineProps<{
  data: ExchangeRateCardData;
}>();

defineEmits<{
  open: [data: ExchangeRateCardData];
}>();
</script>

<style scoped>
.rate-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px;
  text-align: left;
  color: var(--color-text-primary);
  width: 100%;
  cursor: pointer;
}

.rate-card:hover {
  border-color: rgba(125, 163, 255, 0.56);
}

.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h3 {
  margin: 0;
  font-size: 18px;
}

.name {
  margin: 8px 0;
  color: var(--color-text-secondary);
}

.price {
  margin: 4px 0 10px;
  font-size: 30px;
  font-weight: 700;
}

.meta {
  display: flex;
  gap: 14px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.time {
  margin: 10px 0 0;
  color: var(--color-text-muted);
  font-size: 12px;
}

.change {
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 999px;
}

.up {
  color: #5ef7bf;
  background: rgba(30, 201, 143, 0.18);
}

.down {
  color: #ff8dad;
  background: rgba(255, 90, 133, 0.18);
}
</style>
