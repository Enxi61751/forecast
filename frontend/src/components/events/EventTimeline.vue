<template>
  <section class="card timeline-card">
    <header>
      <h3>关键事件时间线</h3>
    </header>

    <ol>
      <li v-for="event in items" :key="event.id">
        <div class="dot" />
        <div class="content">
          <div class="row">
            <h4>{{ event.eventType }}</h4>
            <span class="intensity">强度 {{ typeof event.intensity === 'number' ? event.intensity.toFixed(2) : '--' }}</span>
          </div>
          <p>{{ event.summary }}</p>
          <time>{{ formatTime(event.occurredAt) }}</time>
        </div>
      </li>
    </ol>
  </section>
</template>

<script setup lang="ts">
import type { EventItem } from "@/types/events";

defineProps<{
  items: EventItem[];
}>();

function formatTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")} ${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
}
</script>

<style scoped>
.timeline-card {
  padding: 16px;
}

header h3 {
  margin: 0 0 12px;
}

ol {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
}

li {
  display: grid;
  grid-template-columns: 14px 1fr;
  gap: 10px;
  align-items: flex-start;
}

.dot {
  margin-top: 7px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #6f9dff;
  box-shadow: 0 0 0 6px rgba(111, 157, 255, 0.18);
}

.content {
  border-radius: var(--radius-md);
  border: 1px solid rgba(132, 161, 255, 0.2);
  background: rgba(7, 13, 30, 0.72);
  padding: 10px;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

h4 {
  margin: 0;
  font-size: 14px;
}

.intensity {
  color: #8cb7ff;
  font-size: 12px;
}

p {
  margin: 8px 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

time {
  color: var(--color-text-muted);
  font-size: 12px;
}
</style>
