<template>
  <section class="section-grid">
    <h1 class="page-title">首页</h1>
    <p class="page-subtitle">第三轮前端优化聚焦预测口径收敛、原油预测承接、智能体展示和策略回测展示。</p>

    <AsyncState :status="status" empty-text="功能入口为空" show-retry @retry="init">
      <HeroBanner />
      <section class="entry-grid">
        <FeatureEntryCard v-for="entry in entries" :key="entry.to" :to="entry.to" :title="entry.title" :description="entry.description" />
      </section>
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import HeroBanner from "@/components/home/HeroBanner.vue";
import FeatureEntryCard from "@/components/home/FeatureEntryCard.vue";
import type { LoadStatus } from "@/types/common";

const entries = [
  { to: "/exchange", title: "市场行情", description: "查看当前和近期的 WTI 市场浏览信息，包含卡片概览与多时间范围走势详情。" },
  { to: "/forecast", title: "汇率预测", description: "收敛为汇率 next-day 单点预测展示，保留当前预测主页面的布局与状态区。" },
  { to: "/oil-forecast", title: "原油预测", description: "新增 WTI 原油 next-day 单点预测页面，复用现有预测样式体系并预留解释位。" },
  { to: "/agent-interaction", title: "智能体交互", description: "承接 stagex2 多智能体的日报式输出，用消息流视觉展示各 agent 的观点与理由。" },
  { to: "/backtest", title: "策略回测", description: "新增策略回测展示页，预留收益曲线、风险指标、交易摘要和阶段总结位置。" },
  { to: "/news-events", title: "新闻事件", description: "展示近期新闻、情绪变化和关键事件时间线，为预测和解释模块提供上下文参考。" },
  { to: "/explainability", title: "可解释性", description: "保留现有可解释性图层展示入口，继续作为后端解释结果的承接容器。" }
];

const status = ref<LoadStatus>("loading");

async function init(): Promise<void> {
  status.value = "loading";
  await new Promise((resolve) => setTimeout(resolve, 240));
  status.value = entries.length ? "success" : "empty";
}

onMounted(() => {
  void init();
});
</script>

<style scoped>
.entry-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 1000px) {
  .entry-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .entry-grid {
    grid-template-columns: 1fr;
  }
}
</style>
