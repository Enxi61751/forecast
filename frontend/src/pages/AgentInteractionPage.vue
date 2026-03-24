<template>
  <section class="section-grid">
    <h1 class="page-title">智能体交互</h1>


    <AsyncState
      :status="status"
      :error-message="errorMessage"
      empty-text="当前没有可展示的智能体输出。"
      unavailable-text="智能体日报接口尚未合并到当前分支，页面先以 unavailable 状态承接。"
      show-retry
      @retry="loadFeed"
    >
      <section class="card meta-card">
        <p>As of</p>
        <h3>{{ feed?.asOf || "--" }}</h3>
      </section>

      <AgentFeedList :sections="feed?.sections || []" />

      <ReportPanel
        title="Daily Report Slot"
        :content="feed?.reportBody || ''"
        :can-download="Boolean(feed?.reportBody)"
        @download="downloadReport"
      />
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import ReportPanel from "@/components/common/ReportPanel.vue";
import AgentFeedList from "@/components/agent/AgentFeedList.vue";
import { getAgentFeed } from "@/api";
import type { AgentPageState } from "@/types/agent";
import type { LoadStatus } from "@/types/common";

const status = ref<LoadStatus>("loading");
const errorMessage = ref("加载智能体日报失败");
const feed = ref<AgentPageState | null>(null);

async function loadFeed(): Promise<void> {
  status.value = "loading";

  try {
    const result = await getAgentFeed();

    if (!result.available) {
      status.value = "unavailable";
      return;
    }

    feed.value = result.data;
    status.value = result.data?.sections.some((section) => section.items.length) ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "加载智能体日报失败";
    status.value = "error";
  }
}

function downloadReport(): void {
  if (!feed.value?.reportBody) return;

  const blob = new Blob([feed.value.reportBody], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "agent-daily-report.txt";
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
