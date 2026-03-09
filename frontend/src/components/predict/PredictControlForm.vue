<template>
  <section class="card form-card">
    <div class="field-grid">
      <label class="field">
        <span>预测目标</span>
        <select v-model="target">
          <option value="USD/CNY">USD/CNY</option>
          <option value="EUR/CNY">EUR/CNY</option>
          <option value="JPY/CNY">JPY/CNY</option>
          <option value="WTI">WTI</option>
        </select>
      </label>

      <label class="field">
        <span>时间跨度</span>
        <select v-model="horizon">
          <option value="1d">1d</option>
          <option value="7d">7d</option>
          <option value="30d">30d</option>
        </select>
      </label>
    </div>

    <div class="algo-row">
      <div class="chip-wrap">
        <span class="chip">Model: ForecastModel-V1</span>
        <span class="chip">Algorithm: CEEMDAN</span>
        <span class="chip">Algorithm: LightGBM+TFT</span>
      </div>
      <button class="run-btn" type="button" :disabled="loading" @click="onRun">
        {{ loading ? "运行中..." : "运行预测" }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  loading: boolean;
}>();

const emit = defineEmits<{
  run: [{ target: string; horizon: string }];
}>();

const target = ref("USD/CNY");
const horizon = ref("7d");

function onRun(): void {
  if (props.loading) return;
  emit("run", { target: target.value, horizon: horizon.value });
}
</script>

<style scoped>
.form-card {
  padding: 16px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

select {
  border-radius: 10px;
  border: 1px solid rgba(122, 155, 255, 0.42);
  background: rgba(5, 10, 24, 0.9);
  color: var(--color-text-primary);
  padding: 10px;
}

.algo-row {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  border-radius: 999px;
  border: 1px solid rgba(134, 162, 255, 0.45);
  background: rgba(79, 130, 255, 0.14);
  color: #c7d8ff;
  font-size: 12px;
  padding: 5px 10px;
}

.run-btn {
  border: 1px solid rgba(126, 157, 255, 0.65);
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(79, 130, 255, 0.44), rgba(106, 94, 255, 0.45));
  color: var(--color-text-primary);
  padding: 10px 16px;
  cursor: pointer;
}

.run-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .field-grid {
    grid-template-columns: 1fr;
  }

  .algo-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
