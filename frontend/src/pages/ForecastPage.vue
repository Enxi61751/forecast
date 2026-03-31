<template>
  <section class="section-grid">
    <h1 class="page-title">汇率查询</h1>
    <p class="page-subtitle">
      当前页面展示汇率预测任务的运行状态与结果摘要。
    </p>

    <section class="card control-card">
      <div class="control-grid single">
        <label class="field">
          <span>预测目标</span>
          <select v-model="selectedTarget">
            <option
              v-for="item in targetOptions"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </option>
          </select>
        </label>

        <div class="action-wrap">
          <button
            class="run-btn"
            type="button"
            :disabled="runState.phase === 'running'"
            @click="onRun"
          >
            运行汇率查询
          </button>
        </div>
      </div>

      <div class="tag-row">
        <span class="tag-chip">Scope: Exchange</span>
        <span class="tag-chip">Current branch: existing predict API</span>
      </div>
    </section>

    <section class="card status-card">
      <div class="status-header">
        <h2>运行状态</h2>
        <span>{{ statusTitle }}</span>
      </div>

      <div class="status-steps">
        <div class="status-step" :class="{ active: runState.phase === 'idle' }">未开始</div>
        <div class="status-step" :class="{ active: runState.phase === 'running' }">运行中</div>
        <div class="status-step" :class="{ active: runState.phase === 'success' }">已完成</div>
        <div class="status-step" :class="{ active: runState.phase === 'error' }">失败</div>
      </div>

      <div class="progress-wrap">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${runState.progress}%` }" />
        </div>
        <div class="progress-meta">
          <span>进度 {{ runState.progress }}%</span>
          <span v-if="runState.runId">Run ID: {{ runState.runId }}</span>
        </div>
      </div>
    </section>

    <AsyncState
      :status="resultStatus"
      :error-text="runState.error || '加载汇率结果失败'"
      empty-text="暂无汇率结果"
      show-retry
      @retry="onRun"
    >
      <section class="summary-grid">
        <article class="card summary-card">
          <h3>当前关注品种</h3>
          <p class="summary-main">{{ result?.target || selectedTarget }}</p>
          <p class="summary-sub">{{ targetDescription }}</p>
        </article>

        <article class="card summary-card">
          <h3>生成时间</h3>
          <p class="summary-main summary-time">{{ result?.generatedAt || "-" }}</p>
          <p class="summary-sub">Current branch keeps existing predict API.</p>
        </article>
      </section>

      <section class="card result-card" v-if="result">
        <div class="result-header">
          <h2>汇率结果摘要</h2>
          <span>{{ statusTitle }}</span>
        </div>

        <div class="result-grid">
          <div class="result-item">
            <span class="result-label">趋势判断</span>
            <strong class="result-value">{{ result.summary.trend || "-" }}</strong>
          </div>
          <div class="result-item">
            <span class="result-label">风险提示</span>
            <strong class="result-value">{{ result.summary.risk || "-" }}</strong>
          </div>
          <div class="result-item">
            <span class="result-label">置信度</span>
            <strong class="result-value">
              {{ result.summary.confidence == null ? "-" : formatPercent(result.summary.confidence) }}
            </strong>
          </div>
          <div class="result-item">
            <span class="result-label">说明</span>
            <strong class="result-value">{{ result.summary.explanation || "-" }}</strong>
          </div>
        </div>
      </section>
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import { runPrediction } from "@/api";
import type { LoadStatus } from "@/types/common";
import type { PredictionResult, PredictionRunState } from "@/types/predict";

type TargetOption = {
  label: string;
  value: string;
  description: string;
};

const targetOptions: TargetOption[] = [
  { label: "USD/CNY", value: "USD/CNY", description: "Forecast scope: FX next-day" },
  { label: "EUR/CNY", value: "EUR/CNY", description: "Forecast scope: FX next-day" },
  { label: "JPY/CNY", value: "JPY/CNY", description: "Forecast scope: FX next-day" }
];

const selectedTarget = ref<string>("USD/CNY");
const result = ref<PredictionResult | null>(null);

const runState = ref<PredictionRunState>({
  phase: "idle",
  runId: null,
  progress: 0,
  message: "",
  error: null
});

const targetDescription = computed(() => {
  return targetOptions.find((item) => item.value === selectedTarget.value)?.description ?? "-";
});

const resultStatus = computed<LoadStatus>(() => {
  if (runState.value.phase === "running") {
    return "loading";
  }
  if (runState.value.phase === "error") {
    return "error";
  }
  if (runState.value.phase === "success" && result.value) {
    return "success";
  }
  return "empty";
});

const statusTitle = computed(() => {
  switch (runState.value.phase) {
    case "running":
      return "汇率查询运行中";
    case "success":
      return "汇率查询完成";
    case "error":
      return "汇率查询失败";
    default:
      return "等待运行";
  }
});

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

async function onRun(): Promise<void> {
  runState.value = {
    phase: "running",
    runId: null,
    progress: 20,
    message: "正在请求汇率预测",
    error: null
  };

  try {
    const data = await runPrediction({
      modelType: selectedTarget.value,
      horizon: 1
    });

    result.value = data;
    runState.value = {
      phase: "success",
      runId: data.runId,
      progress: 100,
      message: "汇率查询完成",
      error: null
    };
  } catch (error) {
    console.error(error);
    result.value = null;
    runState.value = {
      phase: "error",
      runId: null,
      progress: 100,
      message: "汇率查询失败",
      error: error instanceof Error ? error.message : "汇率查询失败"
    };
  }
}
</script>

<style scoped>
.control-card,
.status-card,
.result-card,
.summary-card {
  padding: 18px;
}

.control-grid {
  display: grid;
  gap: 16px;
  align-items: end;
}

.control-grid.single {
  grid-template-columns: minmax(0, 1fr) auto;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field span {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.field select {
  border-radius: 14px;
  border: 1px solid rgba(122, 155, 255, 0.42);
  background: rgba(5, 10, 24, 0.9);
  color: var(--color-text-primary);
  padding: 12px 14px;
  font-size: 15px;
}

.action-wrap {
  display: flex;
  justify-content: flex-end;
}

.run-btn {
  min-width: 140px;
  border: 1px solid rgba(122, 155, 255, 0.45);
  background: rgba(102, 123, 255, 0.28);
  color: var(--color-text-primary);
  border-radius: 14px;
  padding: 12px 18px;
  cursor: pointer;
  font-size: 15px;
}

.run-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tag-row {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 13px;
  color: var(--color-text-secondary);
  border: 1px solid rgba(122, 155, 255, 0.28);
  background: rgba(114, 129, 255, 0.12);
}

.status-header,
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.status-header h2,
.result-header h2 {
  margin: 0;
  font-size: 18px;
}

.status-header span,
.result-header span {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.status-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.status-step {
  border: 1px solid rgba(122, 155, 255, 0.22);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  color: var(--color-text-secondary);
  background: rgba(255, 255, 255, 0.02);
}

.status-step.active {
  color: var(--color-text-primary);
  background: rgba(103, 120, 255, 0.22);
  border-color: rgba(122, 155, 255, 0.42);
}

.progress-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-bar {
  width: 100%;
  height: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #5e82ff 0%, #9a67ff 100%);
  transition: width 0.25s ease;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.summary-card h3 {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.summary-main {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  word-break: break-word;
}

.summary-time {
  font-size: 18px;
  line-height: 1.4;
}

.summary-sub {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
}

.result-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.result-value {
  font-size: 16px;
  line-height: 1.5;
  color: var(--color-text-primary);
  word-break: break-word;
}

@media (max-width: 960px) {
  .control-grid.single,
  .summary-grid,
  .result-grid,
  .status-steps {
    grid-template-columns: 1fr;
  }

  .action-wrap {
    justify-content: flex-start;
  }

  .progress-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>