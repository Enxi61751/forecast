<template>
  <section class="section-grid">
    <h1 class="page-title">可解释性分析</h1>
    <p class="page-subtitle">
      展示模型解释结果，包括 SHAP 图、关键特征、最优参数与交叉验证分数。
    </p>

    <section class="card controls-grid">
      <label class="control-item">
        <span>模型选择</span>
        <select v-model="selectedModelKey" @change="onModelChange">
          <option
            v-for="item in modelOptions"
            :key="item.key"
            :value="item.key"
          >
            {{ item.label }}
          </option>
        </select>
      </label>

      <label class="control-item">
        <span>训练日期</span>
        <select
          v-model="selectedTrainDate"
          :disabled="availableDates.length === 0"
        >
          <option
            v-for="date in availableDates"
            :key="date"
            :value="date"
          >
            {{ date }}
          </option>
        </select>
      </label>
    </section>

    <AsyncState
      :status="status"
      :error-text="errorMessage"
      empty-text="该模型暂无可解释性数据"
      show-retry
      @retry="refreshExplainability"
    >
      <template v-if="activeRecord">
        <section class="overview-grid">
          <article class="card metric-card">
            <h3>模型名称</h3>
            <p>{{ explainData?.overview.modelName || "-" }}</p>
          </article>
          <article class="card metric-card">
            <h3>模型类型</h3>
            <p>{{ explainData?.overview.modelType || "-" }}</p>
          </article>
          <article class="card metric-card">
            <h3>训练窗口</h3>
            <p>{{ explainData?.overview.trainLag ?? "-" }}</p>
          </article>
          <article class="card metric-card">
            <h3>更新周期</h3>
            <p>{{ explainData?.overview.updatePeriod ?? "-" }}</p>
          </article>
        </section>

        <section class="content-grid">
  <article class="card image-card">
    <div class="card-header">
      <h2>SHAP Summary Plot</h2>
      <span>{{ activeRecord.trainDate }}</span>
    </div>

    <img
      v-if="hasValidImage(activeRecord.summaryPlot)"
      class="explain-image"
      :src="resolveAssetUrl(activeRecord.summaryPlot)"
      alt="SHAP Summary Plot"
    />
    <div v-else class="image-placeholder">暂无图片</div>

    <p class="card-desc">
      展示不同样本下，各特征对模型输出的影响方向与影响强度。
    </p>
  </article>

  <article class="card image-card">
    <div class="card-header">
      <h2>SHAP Bar Plot</h2>
      <span>{{ activeRecord.sampleCount }} samples</span>
    </div>

    <img
      v-if="hasValidImage(activeRecord.barPlot)"
      class="explain-image"
      :src="resolveAssetUrl(activeRecord.barPlot)"
      alt="SHAP Bar Plot"
    />
    <div v-else class="image-placeholder">暂无图片</div>

    <p class="card-desc">
      展示整体平均影响最大的特征，用于观察模型最关注的因素。
    </p>
  </article>

  <div class="side-column">
    <article class="card param-card">
      <div class="card-header">
        <h2>训练结果摘要</h2>
      </div>

      <div class="param-list">
        <div class="param-row">
          <span>Best CV Score</span>
          <strong>{{ formatValue(activeRecord.bestCvScore) }}</strong>
        </div>
        <div class="param-row">
          <span>Train Date</span>
          <strong>{{ activeRecord.trainDate }}</strong>
        </div>
        <div class="param-row">
          <span>Sample Count</span>
          <strong>{{ activeRecord.sampleCount }}</strong>
        </div>
      </div>

      <h3 class="sub-title">Best Params</h3>
      <div class="params-grid">
        <div
          v-for="(value, key) in activeRecord.bestParams"
          :key="key"
          class="param-chip"
        >
          <span class="param-key">{{ key }}</span>
          <span class="param-value">{{ formatValue(value) }}</span>
        </div>
      </div>
    </article>

    <article class="card feature-card">
      <div class="card-header">
        <h2>关键特征</h2>
      </div>

      <ul class="feature-list">
        <li
          v-for="feature in activeRecord.topFeatures"
          :key="feature.name"
        >
          <span>{{ feature.name }}</span>
          <strong>{{ formatValue(feature.importance) }}</strong>
        </li>
      </ul>

      <p class="card-desc" v-if="activeRecord.conclusion">
        {{ activeRecord.conclusion }}
      </p>
    </article>
  </div>
</section>

        
      </template>
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import { getExplainabilityByModel, getExplainabilityModels } from "@/api";
import type { LoadStatus } from "@/types/common";
import type {
  ExplainabilityModelOption,
  ExplainabilityRecord,
  ExplainabilityResponse
} from "@/types/explainability";

const status = ref<LoadStatus>("loading");
const errorMessage = ref("加载可解释性结果失败");

const modelOptions = ref<ExplainabilityModelOption[]>([]);
const selectedModelKey = ref("");
const selectedTrainDate = ref("");

const explainData = ref<ExplainabilityResponse | null>(null);

const availableDates = computed(() =>
  (explainData.value?.records ?? []).map((item) => item.trainDate)
);

const activeRecord = computed<ExplainabilityRecord | null>(() => {
  const records = explainData.value?.records ?? [];
  if (!records.length) {
    return null;
  }

  return (
    records.find((item) => item.trainDate === selectedTrainDate.value) ??
    records[0] ??
    null
  );
});

function formatValue(value: unknown): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(6);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (value === null || value === undefined) {
    return "-";
  }
  return String(value);
}

function hasValidImage(path: string | null | undefined): boolean {
  return Boolean(path && path.trim());
}

function resolveAssetUrl(path: string): string {
  if (!path || !path.trim()) {
    return "";
  }

  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  const backendBaseUrl =
    (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
    "http://localhost:8080";

  if (path.startsWith("/")) {
    return `${backendBaseUrl}${path}`;
  }

  return `${backendBaseUrl}/${path}`;
}

async function loadModelOptions(): Promise<void> {
  modelOptions.value = await getExplainabilityModels();
  if (!selectedModelKey.value && modelOptions.value.length > 0) {
    selectedModelKey.value = modelOptions.value[0].key;
  }
}

async function loadExplainability(modelKey: string): Promise<void> {
  explainData.value = await getExplainabilityByModel(modelKey);
  const firstDate = explainData.value.records?.[0]?.trainDate ?? "";
  if (!availableDates.value.includes(selectedTrainDate.value)) {
    selectedTrainDate.value = firstDate;
  }
}

async function refreshExplainability(): Promise<void> {
  status.value = "loading";
  try {
    if (!modelOptions.value.length) {
      await loadModelOptions();
    }

    if (!selectedModelKey.value) {
      status.value = "empty";
      return;
    }

    await loadExplainability(selectedModelKey.value);
    status.value = explainData.value?.records?.length ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value =
      error instanceof Error ? error.message : "加载可解释性结果失败";
    status.value = "error";
  }
}

async function onModelChange(): Promise<void> {
  selectedTrainDate.value = "";
  await refreshExplainability();
}

onMounted(() => {
  void refreshExplainability();
});
</script>

<style scoped>
.controls-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 280px));
  gap: 16px;
  padding: 14px;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.control-item select {
  border-radius: 10px;
  border: 1px solid rgba(122, 155, 255, 0.42);
  background: rgba(5, 10, 24, 0.9);
  color: var(--color-text-primary);
  padding: 10px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.metric-card {
  padding: 18px;
}

.metric-card h3 {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.metric-card p {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  word-break: break-word;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.4fr 1.4fr 1fr;
  gap: 16px;
  align-items: start;
}

.image-card,
.param-card,
.feature-card {
  padding: 18px;
}

.side-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
}

.card-header span {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.explain-image {
  width: 100%;
  border-radius: 14px;
  display: block;
  background: rgba(255, 255, 255, 0.04);
}

.image-placeholder {
  width: 100%;
  min-height: 220px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 15px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px dashed rgba(255, 255, 255, 0.12);
}

.card-desc {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.param-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.sub-title {
  margin: 20px 0 12px;
  font-size: 16px;
}

.params-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.param-chip {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
}

.param-key {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.param-value {
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: 13px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feature-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .side-column {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .controls-grid,
  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>