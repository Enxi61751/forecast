<template>
  <section class="section-grid">
    <h1 class="page-title">原油价格预测</h1>


    <PredictControlForm
      :loading="isRunning"
      :target-options="targetOptions"
      :default-target="targetOptions[0].value"
      fixed-horizon-label="Next-day / 1d"
      submit-text="运行原油预测"
      :chips="['Target: WTI futures', 'Model chain: TFT', 'Display: next-day single point']"
      @run="onRun"
    />

    <RunStatusPanel
      :phase="runState.phase"
      :progress="runState.progress"
      :message="runState.message"
      :run-id="runState.runId"
    />

    <AsyncState
      :status="resultStatus"
      loading-text="正在运行原油预测任务..."
      empty-text="请运行 WTI next-day 单点预测。"
      :error-message="runState.error || defaultError"
      unavailable-text="原油预测页面已就绪，扩展字段将随接口完善逐步接入。"
      show-retry
      @retry="rerun"
    >
      <section class="snapshot-grid">
        <article class="card snapshot-card">
          <p>当前/最近市场信息</p>
          <h3>查看市场行情页</h3>
          <RouterLink class="snapshot-link" to="/exchange">前往市场行情</RouterLink>
        </article>
        <article class="card snapshot-card">
          <p>next-day prediction</p>
          <h3>{{ nextDayValue }}</h3>
          <span>{{ nextDayLabel }}</span>
        </article>
        <article class="card snapshot-card">
          <p>生成时间</p>
          <h3>{{ generatedAtText }}</h3>
          <span>Target: {{ prediction?.target || "WTI" }}</span>
        </article>
      </section>

      <ChartPanel
        title="WTI Next-day Prediction"
        :labels="resultLabels"
        :values="resultValues"
        :height="280"
      >
        <template #head-extra>
          <span class="run-tip">{{ runState.message }}</span>
        </template>
      </ChartPanel>

      <PredictSummaryCards
        :trend="prediction?.summary.trend || '--'"
        :risk="prediction?.summary.risk ?? null"
        :confidence="prediction?.summary.confidence ?? null"
      />

      <ReportPanel
        title="Explanation Slot"
        :content="reportContent"
        :can-download="Boolean(reportContent)"
        @download="downloadReport"
      />
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";
import AsyncState from "@/components/common/AsyncState.vue";
import ChartPanel from "@/components/common/ChartPanel.vue";
import ReportPanel from "@/components/common/ReportPanel.vue";
import PredictControlForm from "@/components/predict/PredictControlForm.vue";
import PredictSummaryCards from "@/components/predict/PredictSummaryCards.vue";
import RunStatusPanel from "@/components/predict/RunStatusPanel.vue";
import { getRunStatus, runPrediction } from "@/api";
import type { LoadStatus, SelectOption } from "@/types/common";
import type { PredictionResult, PredictionRunState } from "@/types/predict";

const targetOptions: SelectOption[] = [
  { label: "WTI", value: "WTI" }
];

const defaultError = "原油预测任务失败";

const runState = ref<PredictionRunState>({
  phase: "idle",
  runId: null,
  progress: 0,
  message: "任务未开始",
  error: null
});

const prediction = ref<PredictionResult | null>(null);
const reportContent = ref("");
const lastParams = ref<{ target: string; horizon: string } | null>(null);

const isRunning = computed(() => runState.value.phase === "running");
const pageReady = computed(() => targetOptions.length > 0);

const resultStatus = computed<LoadStatus>(() => {
  if (!pageReady.value) return "unavailable";
  if (runState.value.phase === "running") return "loading";
  if (runState.value.phase === "success") return "success";
  if (runState.value.phase === "error") return "error";
  return "empty";
});

const resultValues = computed(() => prediction.value?.forecast.map((item) => item.value) || []);
const resultLabels = computed(() => prediction.value?.forecast.map((item) => item.time) || []);
const nextDayValue = computed(() => (
  typeof prediction.value?.nextDayPoint?.value === "number" ? prediction.value.nextDayPoint.value.toFixed(4) : "--"
));
const nextDayLabel = computed(() => prediction.value?.nextDayPoint?.time || "D+1");
const generatedAtText = computed(() => prediction.value?.generatedAt || "--");

function resetResultArea(): void {
  prediction.value = null;
  reportContent.value = "";
}

function toHorizonDays(value: string): number {
  const parsed = Number(value.replace("d", ""));
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
}

async function onRun(params: { target: string; horizon: string }): Promise<void> {
  if (isRunning.value) return;

  lastParams.value = params;
  resetResultArea();

  runState.value = {
    phase: "running",
    runId: null,
    progress: 15,
    message: "正在提交原油预测任务",
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

    const result = await runPrediction({
      modelType: params.target,
      horizon: toHorizonDays(params.horizon)
    });

    prediction.value = result;
    reportContent.value = result.reportPreview || "";

    runState.value = {
      phase: "success",
      runId: result.runId,
      progress: 100,
      message: "原油预测完成",
      error: null
    };
  } catch (error) {
    console.error(error);
    runState.value = {
      phase: "error",
      runId: runState.value.runId,
      progress: 100,
      message: "原油预测流程失败",
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
  anchor.download = `oil-forecast-report-${runState.value.runId || Date.now()}.txt`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
</script>

<style scoped>
.snapshot-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.snapshot-card {
  padding: 14px;
  display: grid;
  gap: 8px;
}

.snapshot-card p,
.snapshot-card span {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.snapshot-card h3 {
  margin: 0;
  font-size: 22px;
}

.snapshot-link {
  color: #8ab7ff;
  text-decoration: none;
}

.run-tip {
  color: var(--color-text-secondary);
  font-size: 12px;
}

@media (max-width: 960px) {
  .snapshot-grid {
    grid-template-columns: 1fr;
  }
}
</style>
