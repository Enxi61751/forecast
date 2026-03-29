<template>
  <section class="card decision-panel">
    <header class="panel-head">
      <div>
        <p class="eyebrow">Agent Decisions</p>
        <h2>智能体决策输出 (Agent Decisions)</h2>
      </div>
    </header>

    <div v-if="!entries.length" class="placeholder-box">
      <p>请先运行模拟查看结果。</p>
    </div>

    <div v-else class="decision-list">
      <details v-for="[agentName, decision] in entries" :key="agentName" class="decision-card">
        <summary class="decision-summary">
          <span>{{ agentName }}</span>
          <button class="copy-btn" type="button" @click.stop="copyDecision(agentName, decision)">
            {{ copiedKey === agentName ? "Copied" : "Copy" }}
          </button>
        </summary>
        <pre class="code-block"><code>{{ formatJson(decision) }}</code></pre>
      </details>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  decisions: Record<string, Record<string, unknown>>;
}>();

const copiedKey = ref("");
let copiedTimer: number | null = null;

const entries = computed(() => Object.entries(props.decisions));

function formatJson(value: Record<string, unknown>): string {
  return JSON.stringify(value, null, 2);
}

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

async function copyDecision(agentName: string, decision: Record<string, unknown>): Promise<void> {
  try {
    await copyText(formatJson(decision));
    copiedKey.value = agentName;

    if (copiedTimer) {
      window.clearTimeout(copiedTimer);
    }

    copiedTimer = window.setTimeout(() => {
      copiedKey.value = "";
      copiedTimer = null;
    }, 1800);
  } catch (error) {
    console.error("Failed to copy decision JSON", error);
  }
}
</script>

<style scoped>
.decision-panel {
  padding: 16px;
  display: grid;
  gap: 14px;
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

.decision-list {
  display: grid;
  gap: 12px;
}

.decision-card {
  border-radius: var(--radius-md);
  border: 1px solid rgba(132, 161, 255, 0.18);
  background: rgba(7, 13, 30, 0.62);
  overflow: hidden;
}

.decision-summary {
  list-style: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  cursor: pointer;
  font-weight: 600;
}

.decision-summary::-webkit-details-marker {
  display: none;
}

.code-block {
  margin: 0;
  padding: 0 16px 16px;
  white-space: pre-wrap;
  color: var(--color-text-secondary);
  line-height: 1.6;
  font-size: 13px;
}

.copy-btn {
  border: 1px solid rgba(110, 145, 255, 0.72);
  border-radius: var(--radius-sm);
  background: rgba(79, 130, 255, 0.16);
  color: var(--color-text-primary);
  padding: 6px 10px;
  cursor: pointer;
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
  .decision-summary {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
