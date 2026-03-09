<template>
  <section class="section-grid">
    <h1 class="page-title">可解释性分析</h1>
    <p class="page-subtitle">当前展示占位图结构，后续可替换为真实模型输出。</p>

    <section class="card controls">
      <label>
        <span>模型选择</span>
        <select v-model="model" @change="refreshGraph">
          <option value="Model-1">Model-1</option>
          <option value="Model-2">Model-2</option>
        </select>
      </label>
    </section>

    <AsyncState :status="status" :error-message="errorMessage" empty-text="该模型暂无图数据" show-retry @retry="refreshGraph">
      <ExplainGraphPanel :nodes="graph.nodes" :edges="graph.edges" />
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import ExplainGraphPanel from "@/components/explain/ExplainGraphPanel.vue";
import { mockExplainGraphs } from "@/mocks";
import type { LoadStatus } from "@/types/common";

const model = ref("Model-1");
const status = ref<LoadStatus>("loading");
const errorMessage = ref("加载可解释性图失败");

const graph = computed(() => mockExplainGraphs[model.value] || { nodes: [], edges: [] });

async function refreshGraph(): Promise<void> {
  status.value = "loading";
  try {
    await new Promise((resolve) => setTimeout(resolve, 200));
    status.value = graph.value.nodes.length ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "加载可解释性图失败";
    status.value = "error";
  }
}

onMounted(() => {
  void refreshGraph();
});
</script>

<style scoped>
.controls {
  padding: 14px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--color-text-secondary);
  font-size: 13px;
  max-width: 220px;
}

select {
  border-radius: 10px;
  border: 1px solid rgba(122, 155, 255, 0.42);
  background: rgba(5, 10, 24, 0.9);
  color: var(--color-text-primary);
  padding: 10px;
}
</style>
