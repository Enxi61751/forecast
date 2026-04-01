<template>
  <section class="section-grid">
    <h1 class="page-title">首页</h1>

    <AsyncState :status="status" empty-text="功能入口为空" show-retry @retry="init">
      <HeroBanner />
      <section class="entry-grid">
        <FeatureEntryCard
          v-for="entry in entries"
          :key="entry.to"
          :to="entry.to"
          :title="entry.title"
          :description="entry.description"
        />
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

type HomeEntry = {
  to: string;
  title: string;
  description: string;
};

const entries: HomeEntry[] = [
  {
    to: "/exchange",
    title: "市场行情",
    description: "查看汇率、油价等市场数据的最新展示结果"
  },
  {
    to: "/oil-forecast",
    title: "原油预测",
    description: "查看原油价格预测结果与趋势变化"
  },
  {
    to: "/agent-interaction",
    title: "智能体交互",
    description: "查看多智能体分析过程与交互结果"
  },
  {
    to: "/backtest",
    title: "策略回测",
    description: "查看模型历史表现、收益变化与回测结果"
  },
  {
    to: "/news-events",
    title: "新闻事件",
    description: "查看新闻、事件及其对市场的影响分析"
  },
  {
    to: "/explainability",
    title: "可解释性",
    description: "查看模型解释结果、关键特征与分析摘要"
  }
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