<template>
  <section class="feed-layout">
    <section v-for="section in sections" :key="section.id" class="section-grid">
      <header class="section-head">
        <h2>{{ section.title }}</h2>
        <p>{{ section.items.length }} agents</p>
      </header>
      <div class="feed-grid">
        <AgentFeedCard v-for="item in section.items" :key="item.id" :item="item" />
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import AgentFeedCard from "@/components/agent/AgentFeedCard.vue";
import type { AgentFeedSection } from "@/types/agent";

defineProps<{
  sections: AgentFeedSection[];
}>();
</script>

<style scoped>
.feed-layout,
.section-grid {
  display: grid;
  gap: 14px;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.section-head h2,
.section-head p {
  margin: 0;
}

.section-head p {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.feed-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 980px) {
  .feed-grid {
    grid-template-columns: 1fr;
  }
}
</style>
