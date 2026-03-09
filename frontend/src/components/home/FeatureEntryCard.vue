<template>
  <RouterLink :to="to" class="card entry-card">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <span>进入模块</span>
  </RouterLink>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";

defineProps<{
  to: string;
  title: string;
  description: string;
}>();
</script>

<style scoped>
.entry-card {
  text-decoration: none;
  display: block;
  padding: 18px;
  min-height: 160px;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.entry-card:hover {
  transform: translateY(-3px);
  border-color: rgba(120, 155, 255, 0.55);
}

h3 {
  margin: 0;
  font-size: 18px;
}

p {
  margin: 10px 0 18px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

span {
  color: #8ab7ff;
  font-size: 13px;
}
</style>
