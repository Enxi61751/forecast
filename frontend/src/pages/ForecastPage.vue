<template>
  <section class="section-grid">
    <h1 class="page-title">原油价格预测</h1>
    <p class="page-subtitle">展示经过算法计算后的原油价格预测结果。</p>

    <PredictControlForm :loading="isRunning" @run="onRun" />

    <RunStatusPanel
      :phase="runState.phase"
      :progress="runState.progress"
      :message="runState.message"
      :run-id="runState.runId"
    />

    <AsyncState
      :status="resultStatus"
      loading-text="正在运行预测任务..."
      empty-text="请选择目标和时间跨度后运行预测"
      :error-message="runState.error || defaultError"
      show-retry
      @retry="rerun"
    >
      <ChartPanel
        title="预测结果趋势"
        :labels="resultLabels"
        :values="resultValues"
        :height="280"
        :enable-zoom="true"
      >
        <template #head-extra>
          <span class="run-tip">{{ runState.message }}</span>
        </template>
      </ChartPanel>

      <PredictSummaryCards
        :trend="prediction?.summary.trend || '-'"
        :risk="prediction?.summary.risk || '-'"
        :confidence="prediction?.summary.confidence || 0"
      />

      <ReportPanel
        :title="reportTitle"
        :content="reportContent"
        :can-download="Boolean(reportContent)"
        @download="downloadReport"
      />
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import ChartPanel from "@/components/common/ChartPanel.vue";
import ReportPanel from "@/components/common/ReportPanel.vue";
import PredictControlForm from "@/components/predict/PredictControlForm.vue";
import PredictSummaryCards from "@/components/predict/PredictSummaryCards.vue";
import RunStatusPanel from "@/components/predict/RunStatusPanel.vue";
import { getRunStatus, runPrediction } from "@/api";
import type { LoadStatus } from "@/types/common";
import type { PredictionRunState } from "@/types/predict";

type PagePredictionResult = {
  runId: string;
  forecast: { time: string; value: number }[];
  summary: {
    trend: string;
    risk: string;
    confidence: number;
  };
  reportPreview: string;
};
const defaultError = "预测任务失败";

const runState = ref<PredictionRunState>({
  phase: "idle",
  runId: null,
  progress: 0,
  message: "任务未开始",
  error: null
});

const reportTitle = ref("AI 分析报告");
const reportContent = ref("");
const prediction = ref<PagePredictionResult | null>(null);
const lastParams = ref<{ target: string; horizon: string } | null>(null);

const isRunning = computed(() => runState.value.phase === "running");

const resultStatus = computed<LoadStatus>(() => {
  if (runState.value.phase === "running") return "loading";
  if (runState.value.phase === "success") return "success";
  if (runState.value.phase === "error") return "error";
  return "empty";
});

const resultValues = computed(() => prediction.value?.forecast.map((item) => item.value) || []);
const resultLabels = computed(() => prediction.value?.forecast.map((item) => item.time) || []);

function resetResultArea(): void {
  prediction.value = null;
  reportTitle.value = "AI 分析报告";
  reportContent.value = "";
}

async function onRun(params: { target: string; horizon: string }): Promise<void> {
  if (isRunning.value) return;

  lastParams.value = params;
  resetResultArea();

  runState.value = {
    phase: "running",
    runId: null,
    progress: 15,
    message: "正在提交预测任务",
    error: null
  };

  try {
    const health = await getRunStatus();

    runState.value = {
      phase: "running",
      runId: null,
      progress: 35,
      message: `后端状态：${health.status}`,
      error: null
    };

    const predictRes = await runPrediction({
      modelType: params.target,
      horizon: Number(params.horizon)
    });

    const mappedPrediction: PagePredictionResult = {
      runId: `${Date.now()}`,
      forecast: predictRes.result.map((item) => ({
        time: item.date,
        value: item.value
      })),
      summary: {
        trend: predictRes.result.length >= 2 && predictRes.result[predictRes.result.length - 1].value >= predictRes.result[0].value
          ? "upward"
          : "downward",
        risk: "medium",
        confidence: 0.75
      },
      reportPreview: `模型 ${predictRes.modelType} 已完成预测，共生成 ${predictRes.result.length} 个时间点。`
    };

    prediction.value = mappedPrediction;

    reportTitle.value = "AI 分析报告";
    reportContent.value = mappedPrediction.reportPreview;

    runState.value = {
      phase: "success",
      runId: mappedPrediction.runId,
      progress: 100,
      message: "预测完成",
      error: null
    };
  } catch (error) {
    console.error(error);
    runState.value = {
      phase: "error",
      runId: runState.value.runId,
      progress: 100,
      message: "预测流程失败",
      error: error instanceof Error ? error.message : defaultError
    };
  }
}

function rerun(): void {
  if (!lastParams.value) {
    runState.value = {
      phase: "idle",
      runId: null,
      progress: 0,
      message: "任务未开始",
      error: null
    };
    return;
  }

  void onRun(lastParams.value);
}

function downloadReport(): void {
  if (!reportContent.value) return;

  const blob = new Blob([reportContent.value], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `risk-report-${runState.value.runId || Date.now()}.txt`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
</script>

<style scoped>
.run-tip {
  color: var(--color-text-secondary);
  font-size: 12px;
}
</style>