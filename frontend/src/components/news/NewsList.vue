<template>
  <section class="card list-card">
    <header>
      <h3>近期新闻</h3>
    </header>

    <ul>
      <li v-for="item in items" :key="item.id">
        <div class="headline-row">
          <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
          <StatusBadge :label="badgeLabel(item.sentimentLabel, item.sentimentScore)" :tone="badgeTone(item.sentimentLabel)" />
        </div>
        <p>{{ item.summary }}</p>
        <div class="meta">
          <span>{{ item.source }}</span>
          <span>{{ formatTime(item.publishedAt) }}</span>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import StatusBadge from "@/components/common/StatusBadge.vue";
import type { NewsItem, SentimentLabel } from "@/types/news";

defineProps<{
  items: NewsItem[];
}>();

function badgeTone(label: SentimentLabel): "positive" | "neutral" | "negative" {
  if (label === "Positive") return "positive";
  if (label === "Negative") return "negative";
  return "neutral";
}

function badgeLabel(label: SentimentLabel | undefined, score: number | undefined): string {
  const safeLabel = label ?? "Neutral";
  const safeScore = typeof score === "number" ? score.toFixed(2) : "--";
  return `${safeLabel} ${safeScore}`;
}

function formatTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
</script>

<style scoped>
.list-card {
  padding: 16px;
}

header h3 {
  margin: 0 0 12px;
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

li {
  border-radius: var(--radius-md);
  border: 1px solid rgba(132, 161, 255, 0.22);
  background: rgba(7, 13, 30, 0.72);
  padding: 12px;
}

.headline-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

a {
  text-decoration: none;
  color: var(--color-text-primary);
  font-weight: 600;
}

a:hover {
  color: #88b6ff;
}

p {
  margin: 10px 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.meta {
  display: flex;
  gap: 12px;
  color: var(--color-text-muted);
  font-size: 12px;
}
</style>
