<template>
  <section class="section-grid">
    <h1 class="page-title">实时汇率</h1>
    <p class="page-subtitle">点击卡片查看不同时间范围的趋势详情。</p>

    <AsyncState :status="status" :error-message="errorMessage" empty-text="暂无汇率数据" show-retry @retry="loadRates">
      <section class="rate-grid">
        <ExchangeRateCard v-for="item in rates" :key="item.id" :data="item" @open="openDetail" />
      </section>
    </AsyncState>

    <ExchangeDetailModal
      v-model="showModal"
      :selected="selected"
      :range="range"
      @update:range="range = $event"
    />
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import ExchangeRateCard from "@/components/exchange/ExchangeRateCard.vue";
import ExchangeDetailModal from "@/components/exchange/ExchangeDetailModal.vue";
import { getExchangeRates } from "@/api";
import type { LoadStatus } from "@/types/common";
import type { ExchangeRateCardData, ExchangeTimeRange } from "@/types/exchange";

const status = ref<LoadStatus>("loading");
const errorMessage = ref("获取汇率数据失败");
const rates = ref<ExchangeRateCardData[]>([]);
const selected = ref<ExchangeRateCardData | null>(null);
const showModal = ref(false);
const range = ref<ExchangeTimeRange>("1W");

function openDetail(data: ExchangeRateCardData): void {
  selected.value = data;
  range.value = "1W";
  showModal.value = true;
}

async function loadRates(): Promise<void> {
  status.value = "loading";
  try {
    const data = await getExchangeRates();
    rates.value = data;
    status.value = data.length ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "获取汇率数据失败";
    status.value = "error";
  }
}

onMounted(() => {
  void loadRates();
});
</script>

<style scoped>
.rate-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 1000px) {
  .rate-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .rate-grid {
    grid-template-columns: 1fr;
  }
}
</style>
