<template>
  <section class="section-grid">
    <h1 class="page-title">实时原油价格</h1>
    <p class="page-subtitle">点击卡片查看不同时间范围的趋势详情。</p>

    <AsyncState
      :status="status"
      :error-message="errorMessage"
      empty-text="暂无原油价格数据"
      show-retry
      @retry="loadRates"
    >
      <section class="rate-grid">
        <ExchangeRateCard
          v-for="item in rates"
          :key="item.id"
          :data="item"
          @open="openDetail"
        />
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
const errorMessage = ref("获取原油价格数据失败");
const rates = ref<ExchangeRateCardData[]>([]);
const selected = ref<ExchangeRateCardData | null>(null);
const showModal = ref(false);
const range = ref<ExchangeTimeRange>("1W");

function openDetail(data: ExchangeRateCardData): void {
  selected.value = data;
  range.value = "1W";
  showModal.value = true;
}

function buildTrend(baseRate: number): Record<ExchangeTimeRange, number[]> {
  return {
    "1W": [
      Number((baseRate - 0.08).toFixed(2)),
      Number((baseRate - 0.04).toFixed(2)),
      Number((baseRate - 0.02).toFixed(2)),
      Number(baseRate.toFixed(2)),
      Number((baseRate + 0.01).toFixed(2)),
      Number((baseRate + 0.03).toFixed(2)),
      Number((baseRate + 0.02).toFixed(2))
    ],
    "1M": [
      Number((baseRate - 0.15).toFixed(2)),
      Number((baseRate - 0.10).toFixed(2)),
      Number((baseRate - 0.05).toFixed(2)),
      Number(baseRate.toFixed(2))
    ],
    "6M": [
      Number((baseRate - 0.30).toFixed(2)),
      Number((baseRate - 0.22).toFixed(2)),
      Number((baseRate - 0.12).toFixed(2)),
      Number((baseRate - 0.06).toFixed(2)),
      Number(baseRate.toFixed(2)),
      Number((baseRate + 0.08).toFixed(2))
    ]
  };
}

function buildLabels(date: string): Record<ExchangeTimeRange, string[]> {
  return {
    "1W": ["D1", "D2", "D3", "D4", "D5", "D6", "D7"],
    "1M": ["W1", "W2", "W3", "W4"],
    "6M": ["M1", "M2", "M3", "M4", "M5", date]
  };
}

async function loadRates(): Promise<void> {
  status.value = "loading";
  try {
    const res = await getExchangeRates();

    rates.value = res.list.map((item, index) => {
      const trend = buildTrend(item.rate);
      const latestWeek = trend["1W"];
      const first = latestWeek[0];
      const last = latestWeek[latestWeek.length - 1];
      const change = Number((last - first).toFixed(2));

      return {
        id: `oil-${index}`,
        pair: "WTI/USD",
        name: "原油价格",
        price: item.rate,
        change,
        high: Math.max(...latestWeek),
        low: Math.min(...latestWeek),
        updatedAt: item.date,
        trend,
        labels: buildLabels(item.date)
      };
    });

    status.value = rates.value.length ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "获取原油价格数据失败";
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