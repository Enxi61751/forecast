<template>
  <header class="nav-wrap">
    <div class="nav-inner">
      <RouterLink class="brand" to="/">RiskSight</RouterLink>
      <nav class="nav-links">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="link" active-class="is-active">
          {{ item.label }}
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from "vue-router";

const navItems = [
  { to: "/", label: "首页" },
  { to: "/exchange", label: "市场行情" },
  { to: "/forecast", label: "汇率查询" },
  { to: "/oil-forecast", label: "原油预测" },
  { to: "/agent-interaction", label: "智能体交互" },
  { to: "/backtest", label: "策略回测" },
  { to: "/news-events", label: "新闻事件" },
  { to: "/explainability", label: "可解释性" }
];
</script>

<style scoped>
.nav-wrap {
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(10px);
  background: rgba(9, 14, 30, 0.72);
  border-bottom: 1px solid var(--color-border);
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  text-decoration: none;
  font-size: 22px;
  letter-spacing: 0.6px;
  color: var(--color-text-primary);
  font-weight: 700;
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
}

.link {
  text-decoration: none;
  color: var(--color-text-secondary);
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.link:hover {
  color: var(--color-text-primary);
  background: rgba(80, 124, 255, 0.18);
}

.is-active {
  color: var(--color-text-primary);
  background: linear-gradient(135deg, rgba(80, 124, 255, 0.28), rgba(99, 102, 241, 0.35));
  border: 1px solid rgba(115, 145, 255, 0.52);
}

@media (max-width: 768px) {
  .nav-inner {
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-links {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
