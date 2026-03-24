<template>
  <article class="card agent-card">
    <header class="agent-head">
      <div>
        <p class="eyebrow">{{ item.role }}</p>
        <h3>{{ item.agentName }}</h3>
      </div>
      <span :class="['direction-chip', directionTone]">{{ directionText }}</span>
    </header>

    <div class="meta-grid">
      <div class="meta-block">
        <span>风险态度</span>
        <strong>{{ item.riskAttitude || "Unavailable" }}</strong>
      </div>
      <div class="meta-block">
        <span>置信度</span>
        <strong>{{ confidenceText }}</strong>
      </div>
      <div class="meta-block">
        <span>更新时间</span>
        <strong>{{ item.updatedAt || "--" }}</strong>
      </div>
    </div>

    <section class="content-block">
      <h4>理由</h4>
      <p>{{ item.rationale || "当前分支尚未返回 agent rationale。" }}</p>
    </section>

    <section class="content-block">
      <h4>记忆 / 备注</h4>
      <p>{{ item.memory || item.remark || "当前分支尚未返回 memory 或 remark 字段。" }}</p>
    </section>

    <div v-if="item.tags.length" class="tag-row">
      <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { AgentFeedItem } from "@/types/agent";

const props = defineProps<{
  item: AgentFeedItem;
}>();

const directionText = computed(() => props.item.direction || "Direction pending");
const confidenceText = computed(() => (
  typeof props.item.confidence === "number" ? `${(props.item.confidence * 100).toFixed(1)}%` : "Unavailable"
));

const directionTone = computed(() => {
  const value = (props.item.direction || "").toLowerCase();
  if (value.includes("bull") || value.includes("long") || value.includes("buy")) {
    return "positive";
  }

  if (value.includes("bear") || value.includes("short") || value.includes("sell")) {
    return "negative";
  }

  return "neutral";
});
</script>

<style scoped>
.agent-card {
  padding: 16px;
  display: grid;
  gap: 14px;
}

.agent-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--color-text-secondary);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

h3,
h4 {
  margin: 0;
}

.direction-chip {
  border-radius: 999px;
  border: 1px solid rgba(136, 163, 255, 0.35);
  padding: 6px 10px;
  font-size: 12px;
  white-space: nowrap;
}

.direction-chip.positive {
  color: #7ef0c5;
  background: rgba(30, 201, 143, 0.14);
}

.direction-chip.negative {
  color: #ff9eb7;
  background: rgba(255, 90, 133, 0.14);
}

.direction-chip.neutral {
  color: #d9e4ff;
  background: rgba(125, 157, 255, 0.14);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.meta-block {
  border-radius: var(--radius-md);
  border: 1px solid rgba(132, 161, 255, 0.18);
  background: rgba(7, 13, 30, 0.62);
  padding: 10px;
}

.meta-block span {
  display: block;
  color: var(--color-text-secondary);
  font-size: 12px;
  margin-bottom: 6px;
}

.meta-block strong {
  font-size: 14px;
}

.content-block {
  display: grid;
  gap: 8px;
}

.content-block p {
  margin: 0;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  border-radius: 999px;
  background: rgba(79, 130, 255, 0.14);
  border: 1px solid rgba(134, 162, 255, 0.3);
  color: #c7d8ff;
  font-size: 12px;
  padding: 4px 10px;
}

@media (max-width: 780px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }

  .agent-head {
    flex-direction: column;
  }
}
</style>
