<template>
  <section class="section-grid">
    <h1 class="page-title">智能体交互</h1>

    <SimulationControlBar
      v-model="iterationInput"
      :loading="simulationLoading"
      :error="simulationError"
      @simulate="handleSimulate"
      @iterate="handleIterate"
    />

    <ReportPanel
      title="总说明 (Overall Summary)"
      :content="summaryContent"
      :placeholder="summaryPlaceholder"
      :can-download="Boolean(summaryContent)"
      @download="downloadSummary"
    />

    <AgentDecisionJsonBlock :decisions="simulationDecisions" />

    <ParameterCorrectionBlock
      :correction-params="simulationCorrectionParams"
      @copy-to-input="handleCopyToInput"
    />

    <AsyncState
      :status="detailStatus"
      :error-message="errorMessage"
      :empty-text="detailEmptyText"
      unavailable-text="智能体日报接口尚未合并到当前分支，页面先以 unavailable 状态承接。"
      show-retry
      @retry="loadFeed"
    >
      <section class="section-grid">
        <header class="detail-head">
          <div>
            <p class="detail-eyebrow">{{ detailEyebrow }}</p>
            <h2>{{ detailTitle }}</h2>
          </div>
        </header>

        <section class="card meta-card">
          <p>As of</p>
          <h3>{{ detailAsOf || "--" }}</h3>
        </section>

        <AgentFeedList :sections="detailSections" />
      </section>
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import ReportPanel from "@/components/common/ReportPanel.vue";
import AgentFeedList from "@/components/agent/AgentFeedList.vue";
import AgentDecisionJsonBlock from "@/components/agent/AgentDecisionJsonBlock.vue";
import ParameterCorrectionBlock from "@/components/agent/ParameterCorrectionBlock.vue";
import SimulationControlBar from "@/components/agent/SimulationControlBar.vue";
import { getAgentFeed, iterateWithParams, simulateMarket } from "@/api";
import { adaptSimulationResponse } from "@/api/adapters/agentAdapter";
import type { AgentFeedSection, AgentPageState } from "@/types/agent";
import type { LoadStatus } from "@/types/common";

const feedStatus = ref<LoadStatus>("loading");
const errorMessage = ref("加载智能体日报失败");
const feed = ref<AgentPageState | null>(null);
const simulationLoading = ref(false);
const simulationError = ref("");
const simulationResult = ref<ReturnType<typeof adaptSimulationResponse> | null>(null);
const iterationInput = ref("");
const lastSimulationAt = ref<string | null>(null);

const summaryContent = computed(() => simulationResult.value?.summary || "");
const summaryPlaceholder = "请先运行模拟查看结果。";
const simulationDecisions = computed(() => simulationResult.value?.decisions || {});
const simulationCorrectionParams = computed(() => simulationResult.value?.correctionParams || {});
const detailStatus = computed<LoadStatus>(() => {
  if (simulationResult.value) {
    return simulationResult.value.feedItems.length ? "success" : "empty";
  }

  return feedStatus.value;
});
const detailEmptyText = computed(() => (
  simulationResult.value ? "当前模拟结果没有可展示的详细智能体输出。" : "当前没有可展示的智能体输出。"
));
const detailTitle = computed(() => (simulationResult.value ? "模拟详细视图" : "日报详细视图"));
const detailEyebrow = computed(() => (simulationResult.value ? "Simulation Detail" : "Daily Feed"));
const detailAsOf = computed(() => lastSimulationAt.value || feed.value?.asOf || null);
const detailSections = computed<AgentFeedSection[]>(() => {
  if (simulationResult.value?.feedItems.length) {
    return [
      {
        id: "simulation-detail",
        title: "模拟详细视图",
        items: simulationResult.value.feedItems
      }
    ];
  }

  return feed.value?.sections || [];
});

async function loadFeed(): Promise<void> {
  feedStatus.value = "loading";

  try {
    const result = await getAgentFeed();

    if (!result.available) {
      feedStatus.value = "unavailable";
      return;
    }

    feed.value = result.data;
    feedStatus.value = result.data?.sections.some((section) => section.items.length) ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "加载智能体日报失败";
    feedStatus.value = "error";
  }
}

async function handleSimulate(): Promise<void> {
  simulationLoading.value = true;
  simulationError.value = "";

  try {
    const result = await simulateMarket();
    simulationResult.value = adaptSimulationResponse(result);
    lastSimulationAt.value = new Date().toLocaleString("zh-CN", { hour12: false });
  } catch (error) {
    console.error(error);
    simulationError.value = error instanceof Error ? error.message : "运行模拟失败";
  } finally {
    simulationLoading.value = false;
  }
}

async function handleIterate(params: Record<string, unknown>): Promise<void> {
  simulationLoading.value = true;
  simulationError.value = "";

  try {
    const result = await iterateWithParams(params);
    simulationResult.value = adaptSimulationResponse(result);
    lastSimulationAt.value = new Date().toLocaleString("zh-CN", { hour12: false });
  } catch (error) {
    console.error(error);
    simulationError.value = error instanceof Error ? error.message : "运行迭代失败";
  } finally {
    simulationLoading.value = false;
  }
}

function handleCopyToInput(value: string): void {
  iterationInput.value = value;
  simulationError.value = "";
}

function downloadSummary(): void {
  if (!summaryContent.value) {
    return;
  }

  const blob = new Blob([summaryContent.value], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "agent-simulation-summary.txt";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

onMounted(() => {
  void loadFeed();
});
</script>

<style scoped>
.detail-head h2,
.detail-eyebrow {
  margin: 0;
}

.detail-eyebrow {
  margin-bottom: 6px;
  color: var(--color-text-secondary);
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.meta-card {
  padding: 14px;
}

.meta-card p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.meta-card h3 {
  margin: 8px 0 0;
}
</style>
