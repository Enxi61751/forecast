<template>
  <section class="section-grid">
    <h1 class="page-title">汇率预测</h1>
    <p class="page-subtitle">前端只负责请求与展示，算法计算由后端完成。</p>

    <PredictControlForm :loading="isRunning" @run="onRun" />

    <RunStatusPanel :phase="runState.phase" :progress="runState.progress" :message="runState.message" :run-id="runState.runId" />

    <AsyncState
      :status="resultStatus"
      loading-text="正在运行预测任务..."
      empty-text="请选择目标和时间跨度后运行预测"
      :error-message="runState.error || defaultError"
      show-retry
      @retry="rerun"
    >
      <ChartPanel title="预测结果趋势" :labels="resultLabels" :values="resultValues" :height="280" :enable-zoom="true">
        <template #head-extra>
          <span class="run-tip">{{ runState.message }}</span>
        </template>
      </ChartPanel>

      <PredictSummaryCards
        :trend="prediction?.summary.trend || '-'"
        :risk="prediction?.summary.risk || '-'"
        :confidence="prediction?.summary.confidence || 0"
      />

      <ReportPanel :title="reportTitle" :content="reportContent" :can-download="Boolean(reportContent)" @download="downloadReport" />
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
import { generateReport, getReport, getRunStatus, runPrediction } from "@/api";
import type { LoadStatus } from "@/types/common";
import type { PredictionResult, PredictionRunState, RunStatus } from "@/types/predict";

const defaultError = "预测任务失败";
const pollingIntervalMs = 650;
const maxPollingAttempts = 8;

const runState = ref<PredictionRunState>({
  phase: "idle",
  runId: null,
  progress: 0,
  message: "任务未开始",
  error: null
});
const reportTitle = ref("AI 分析报告");
const reportContent = ref("");
const prediction = ref<PredictionResult | null>(null);
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

async function sleep(ms: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForTerminalStatus(runId: string): Promise<RunStatus> {
  let last: RunStatus = {
    runId,
    stage: "running",
    progress: runState.value.progress,
    message: runState.value.message
  };

  for (let attempt = 0; attempt < maxPollingAttempts; attempt += 1) {
    const status = await getRunStatus(runId);
    last = status;

    runState.value = {
      phase: "running",
      runId,
      progress: Math.max(0, Math.min(100, status.progress)),
      message: status.message,
      error: null
    };

    if (status.stage === "completed" || status.stage === "failed") {
      return status;
    }

    await sleep(pollingIntervalMs);
  }

  throw new Error("运行状态查询超时，请稍后重试");
}

async function onRun(params: { target: string; horizon: string }): Promise<void> {
  if (isRunning.value) return;
  lastParams.value = params;
  resetResultArea();

  runState.value = {
    phase: "running",
    runId: null,
    progress: 8,
    message: "正在提交预测任务",
    error: null
  };

  try {
    const runResult = await runPrediction({
      target: params.target,
      horizon: params.horizon,
      payload: {
        model: "ForecastModel-V1",
        algorithms: ["CEEMDAN", "LightGBM+TFT"]
      },
      asOf: new Date().toISOString()
    });

    runState.value = {
      phase: "running",
      runId: runResult.runId,
      progress: 20,
      message: "预测任务已创建，正在获取运行状态",
      error: null
    };

    const terminalStatus = await waitForTerminalStatus(runResult.runId);
    if (terminalStatus.stage === "failed") {
      runState.value = {
        phase: "error",
        runId: runResult.runId,
        progress: terminalStatus.progress,
        message: terminalStatus.message,
        error: terminalStatus.message
      };
      return;
    }

    prediction.value = runResult;
    runState.value = {
      phase: "running",
      runId: runResult.runId,
      progress: 92,
      message: "预测完成，正在生成报告",
      error: null
    };

    const reportId = await generateReport(runResult.runId);
    const report = await getReport(reportId);
    reportTitle.value = report.title;
    reportContent.value = report.content || runResult.reportPreview;

    if (!reportContent.value) {
      reportContent.value = runResult.reportPreview;
    }

    runState.value = {
      phase: "success",
      runId: runResult.runId,
      progress: 100,
      message: "预测与报告生成完成",
      error: null
    };
  } catch (error) {
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
