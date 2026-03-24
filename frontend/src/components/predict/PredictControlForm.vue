<template>
  <section class="card form-card">
    <div class="field-grid">
      <label class="field">
        <span>{{ targetLabel }}</span>
        <select v-model="target" :disabled="targetOptions.length === 1">
          <option v-for="option in targetOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>

      <label class="field">
        <span>预测口径</span>
        <input :value="fixedHorizonLabel" type="text" readonly />
      </label>
    </div>

    <div class="algo-row">
      <div class="chip-wrap">
        <span v-for="chip in chips" :key="chip" class="chip">{{ chip }}</span>
      </div>
      <button class="run-btn" type="button" :disabled="loading" @click="onRun">
        {{ loading ? "运行中..." : submitText }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import type { SelectOption } from "@/types/common";

const props = withDefaults(
  defineProps<{
    loading: boolean;
    targetOptions: SelectOption[];
    defaultTarget?: string;
    fixedHorizonLabel?: string;
    submitText?: string;
    targetLabel?: string;
    chips?: string[];
  }>(),
  {
    defaultTarget: "",
    fixedHorizonLabel: "Next-day / 1d",
    submitText: "运行预测",
    targetLabel: "预测目标",
    chips: () => ["Display: next-day single point"]
  }
);

const emit = defineEmits<{
  run: [{ target: string; horizon: string }];
}>();

const target = ref("");

watch(
  () => [props.defaultTarget, props.targetOptions] as const,
  ([defaultTarget, options]) => {
    target.value = defaultTarget || options[0]?.value || "";
  },
  { immediate: true, deep: true }
);

function onRun(): void {
  if (props.loading || !target.value) return;
  emit("run", { target: target.value, horizon: "1d" });
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

select,
input {
  border-radius: 10px;
  border: 1px solid rgba(122, 155, 255, 0.42);
  background: rgba(5, 10, 24, 0.9);
  color: var(--color-text-primary);
  padding: 10px;
}

input[readonly] {
  cursor: default;
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
