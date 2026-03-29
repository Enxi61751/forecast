<template>
  <section class="card correction-panel">
    <header class="panel-head">
      <div>
        <p class="eyebrow">Parameter Correction</p>
        <h2>参数校正输出 (Parameter Correction)</h2>
      </div>
      <div v-if="hasContent" class="action-row">
        <button class="action-btn" type="button" @click="copyCorrection">
          {{ copied ? "Copied" : "Copy" }}
        </button>
        <button class="action-btn" type="button" @click="emitCopyToInput">
          Copy to Iteration Input
        </button>
      </div>
    </header>

    <div v-if="!hasContent" class="placeholder-box">
      <p>请先运行模拟查看结果。</p>
    </div>

    <pre v-else class="code-block"><code>{{ formattedCorrection }}</code></pre>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  correctionParams: Record<string, unknown>;
}>();

const emit = defineEmits<{
  "copy-to-input": [value: string];
}>();

const copied = ref(false);
let copiedTimer: number | null = null;

const hasContent = computed(() => Object.keys(props.correctionParams).length > 0);
const formattedCorrection = computed(() => JSON.stringify(props.correctionParams, null, 2));

async function copyText(value: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.setAttribute("readonly", "true");
  textarea.style.position = "absolute";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}

function setCopiedState(): void {
  copied.value = true;

  if (copiedTimer) {
    window.clearTimeout(copiedTimer);
  }

  copiedTimer = window.setTimeout(() => {
    copied.value = false;
    copiedTimer = null;
  }, 1800);
}

async function copyCorrection(): Promise<void> {
  try {
    await copyText(formattedCorrection.value);
    setCopiedState();
  } catch (error) {
    console.error("Failed to copy correction params", error);
  }
}

function emitCopyToInput(): void {
  emit("copy-to-input", formattedCorrection.value);
}
</script>

<style scoped>
.correction-panel {
  padding: 16px;
  display: grid;
  gap: 14px;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.panel-head h2,
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

.action-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  border: 1px solid rgba(110, 145, 255, 0.72);
  border-radius: var(--radius-sm);
  background: rgba(79, 130, 255, 0.16);
  color: var(--color-text-primary);
  padding: 8px 12px;
  cursor: pointer;
}

.code-block {
  margin: 0;
  border-radius: var(--radius-md);
  border: 1px solid rgba(118, 153, 255, 0.22);
  background: rgba(8, 12, 28, 0.75);
  padding: 12px;
  white-space: pre-wrap;
  color: var(--color-text-secondary);
  line-height: 1.62;
  font-size: 13px;
}

.placeholder-box {
  border-radius: var(--radius-md);
  border: 1px dashed rgba(118, 155, 255, 0.42);
  background: rgba(14, 23, 52, 0.6);
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  text-align: center;
  padding: 16px;
}

@media (max-width: 640px) {
  .panel-head {
    flex-direction: column;
  }

  .action-row {
    width: 100%;
  }

  .action-btn {
    flex: 1;
  }
}
</style>
