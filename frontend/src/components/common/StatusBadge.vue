<template>
  <span class="badge" :class="toneClass">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    label: string;
    tone?: "positive" | "negative" | "neutral";
  }>(),
  {
    tone: "neutral"
  }
);

const toneClass = computed(() => `tone-${props.tone}`);
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  border-radius: 999px;
  padding: 4px 10px;
  border: 1px solid transparent;
}

.tone-positive {
  color: #5ef7bf;
  background: rgba(30, 201, 143, 0.2);
  border-color: rgba(30, 201, 143, 0.4);
}

.tone-negative {
  color: #ff8dad;
  background: rgba(255, 90, 133, 0.2);
  border-color: rgba(255, 90, 133, 0.45);
}

.tone-neutral {
  color: #bed2ff;
  background: rgba(79, 130, 255, 0.2);
  border-color: rgba(106, 94, 255, 0.4);
}
</style>
