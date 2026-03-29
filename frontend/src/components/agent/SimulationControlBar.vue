<template>
  <section class="card control-bar">
    <div class="control-head">
      <div>
        <p class="eyebrow">Simulation Controls</p>
        <h2>模拟控制台</h2>
      </div>
      <button class="primary-btn" type="button" :disabled="loading" @click="$emit('simulate')">
        <span v-if="loading" class="spinner" />
        <span>{{ loading ? "运行中..." : "一键模拟市场 (Simulate Market)" }}</span>
      </button>
    </div>

    <label class="input-group" for="iteration-input">
      <span>迭代参数输入 (Iteration Parameters)</span>
      <textarea
        id="iteration-input"
        :value="modelValue"
        :disabled="loading"
        rows="8"
        placeholder="{&#10;  &quot;positionSize&quot;: 0.16,&#10;  &quot;hedgeRatio&quot;: 0.42&#10;}"
        @input="handleInput"
      />
    </label>

    <div class="control-footer">
      <button class="secondary-btn" type="button" :disabled="loading" @click="handleIterate">
        <span v-if="loading" class="spinner" />
        <span>{{ loading ? "运行中..." : "运行迭代 (Run Iteration)" }}</span>
      </button>
      <p v-if="displayError" class="error-text">{{ displayError }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = withDefaults(
  defineProps<{
    modelValue?: string;
    loading: boolean;
    error: string;
  }>(),
  {
    modelValue: "",
    error: ""
  }
);

const emit = defineEmits<{
  simulate: [];
  iterate: [params: Record<string, unknown>];
  "update:modelValue": [value: string];
}>();

const validationError = ref("");

const displayError = computed(() => validationError.value || props.error);

function handleInput(event: Event): void {
  const target = event.target as HTMLTextAreaElement;
  validationError.value = "";
  emit("update:modelValue", target.value);
}

function handleIterate(): void {
  validationError.value = "";

  try {
    const parsed = JSON.parse(props.modelValue || "");
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      validationError.value = "Invalid JSON format";
      return;
    }

    emit("iterate", parsed as Record<string, unknown>);
  } catch {
    validationError.value = "Invalid JSON format";
  }
}
</script>

<style scoped>
.control-bar {
  padding: 16px;
  display: grid;
  gap: 14px;
}

.control-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.control-head h2,
.eyebrow {
  margin: 0;
}

.eyebrow {
  margin-bottom: 6px;
  color: var(--color-text-secondary);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.input-group {
  display: grid;
  gap: 8px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.input-group textarea {
  width: 100%;
  border: 1px solid rgba(118, 153, 255, 0.22);
  border-radius: var(--radius-md);
  background: rgba(8, 12, 28, 0.75);
  color: var(--color-text-primary);
  padding: 12px;
  resize: vertical;
  min-height: 180px;
  font: inherit;
  line-height: 1.6;
}

.primary-btn,
.secondary-btn {
  border: 1px solid rgba(110, 145, 255, 0.72);
  border-radius: var(--radius-sm);
  background: rgba(79, 130, 255, 0.16);
  color: var(--color-text-primary);
  padding: 10px 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
}

.primary-btn:disabled,
.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.error-text {
  margin: 0;
  color: var(--color-negative);
  font-size: 14px;
}

.spinner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(239, 244, 255, 0.3);
  border-top-color: var(--color-text-primary);
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .control-head {
    flex-direction: column;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
  }

  .control-footer {
    align-items: stretch;
  }
}
</style>
