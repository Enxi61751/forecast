<template>
  <section class="section-grid">
    <h1 class="page-title">策略回测</h1>


    <AsyncState
      :status="status"
      :error-message="errorMessage"
      empty-text="当前没有可展示的回测结果。"
      unavailable-text="策略回测接口尚未合并到当前分支，页面先以 unavailable 状态承接。"
      show-retry
      @retry="loadBacktest"
    >
      <BacktestSummaryPanel
        :strategy-name="backtest?.strategyName || null"
        :benchmark-name="backtest?.benchmarkName || null"
        :period-label="backtest?.periodLabel || null"
        :notes="backtest?.notes || null"
        :trade-summary="backtest?.tradeSummary || null"
        :period-summary="backtest?.periodSummary || null"
      />

      <BacktestMetricCards v-if="backtest?.metrics.length" :metrics="backtest.metrics" />

      <ChartPanel
        title="Cumulative Return Curve"
        :labels="cumulativeLabels"
        :values="cumulativeValues"
        :height="280"
        :enable-zoom="true"
      />

      <ChartPanel
        title="Drawdown Curve"
        :labels="drawdownLabels"
        :values="drawdownValues"
        :height="240"
        :enable-zoom="true"
      />
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import ChartPanel from "@/components/common/ChartPanel.vue";
import BacktestMetricCards from "@/components/backtest/BacktestMetricCards.vue";
import BacktestSummaryPanel from "@/components/backtest/BacktestSummaryPanel.vue";
import { getBacktestSummary } from "@/api";
import type { LoadStatus } from "@/types/common";
import type { BacktestSummary } from "@/types/backtest";

const status = ref<LoadStatus>("loading");
const errorMessage = ref("加载回测结果失败");
const backtest = ref<BacktestSummary | null>(null);

const cumulativeLabels = computed(() => backtest.value?.cumulativeReturn.map((item) => item.label) || []);
const cumulativeValues = computed(() => backtest.value?.cumulativeReturn.map((item) => item.value) || []);
const drawdownLabels = computed(() => backtest.value?.drawdownCurve.map((item) => item.label) || []);
const drawdownValues = computed(() => backtest.value?.drawdownCurve.map((item) => item.value) || []);

async function loadBacktest(): Promise<void> {
  status.value = "loading";

  try {
    const result = await getBacktestSummary();

    if (!result.available) {
      status.value = "unavailable";
      return;
    }

    backtest.value = result.data;
    const hasContent = Boolean(
      result.data?.metrics.length ||
      result.data?.cumulativeReturn.length ||
      result.data?.drawdownCurve.length
    );
    status.value = hasContent ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "加载回测结果失败";
    status.value = "error";
  }
}

onMounted(() => {
  void loadBacktest();
});
</script>
