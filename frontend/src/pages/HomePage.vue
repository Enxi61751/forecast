<template>
  <section class="section-grid">
    <h1 class="page-title">首页</h1>
    <p class="page-subtitle">可运行、可展示、可后续联调的金融风险预测前端框架。</p>

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
  { to: "/exchange", title: "实时汇率", description: "查看主要货币对实时卡片和趋势详情弹窗。" },
  { to: "/forecast", title: "汇率预测", description: "运行预测任务，展示图表、摘要和报告区域。" },
  { to: "/news-events", title: "新闻与事件", description: "展示近期新闻、情绪分值和极端事件时间线。" },
  { to: "/explainability", title: "可解释性分析", description: "展示模型图结构、关系权重和图例说明。" }
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
