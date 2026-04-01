<template>
  <section class="section-grid">
    <h1 class="page-title">市场行情</h1>

    <section class="card market-note">
      <div>
        <h3>这里展示的是实时油价市场数据</h3>
        <p>页面会自动轮询后端接口，获取最新油价与历史走势</p>
      </div>
      <RouterLink class="market-link" to="/oil-forecast">前往原油预测</RouterLink>
    </section>

    <AsyncState
      :status="status"
      :error-message="errorMessage"
      empty-text="暂无原油市场数据"
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
import { onBeforeUnmount, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import AsyncState from "@/components/common/AsyncState.vue";
import ExchangeRateCard from "@/components/exchange/ExchangeRateCard.vue";
import ExchangeDetailModal from "@/components/exchange/ExchangeDetailModal.vue";
import { getExchangeRates } from "@/api";
import type { ExchangeHistoryPoint, ExchangeItem } from "@/api/exchange";
import type { LoadStatus } from "@/types/common";
import type { ExchangeRateCardData, ExchangeTimeRange } from "@/types/exchange";

const status = ref<LoadStatus>("loading");
const errorMessage = ref("获取市场数据失败");
const rates = ref<ExchangeRateCardData[]>([]);
const selected = ref<ExchangeRateCardData | null>(null);
const showModal = ref(false);
const range = ref<ExchangeTimeRange>("1W");

let refreshTimer: number | null = null;
const REFRESH_INTERVAL_MS = 30000;

function openDetail(data: ExchangeRateCardData): void {
  selected.value = data;
  range.value = "1W";
  showModal.value = true;
}

function toTrend(points: ExchangeHistoryPoint[] | undefined): number[] {
  if (!points?.length) {
    return [];
  }
  return points.map((point) => Number(Number(point.value).toFixed(4)));
}

function toLabels(points: ExchangeHistoryPoint[] | undefined): string[] {
  if (!points?.length) {
    return [];
  }
  return points.map((point) => point.date);
}

function normalizeItem(item: ExchangeItem, index: number): ExchangeRateCardData {
  return {
    id: `${item.symbol}-${index}`,
    pair: item.symbol,
    name: item.name,
    price: Number(Number(item.close).toFixed(4)),
    change: Number(Number(item.change).toFixed(4)),
    high: Number(Number(item.high).toFixed(4)),
    low: Number(Number(item.low).toFixed(4)),
    updatedAt: item.date,
    trend: {
      "1W": toTrend(item.history?.["1W"]),
      "1M": toTrend(item.history?.["1M"]),
      "6M": toTrend(item.history?.["6M"])
    },
    labels: {
      "1W": toLabels(item.history?.["1W"]),
      "1M": toLabels(item.history?.["1M"]),
      "6M": toLabels(item.history?.["6M"])
    }
  };
}

async function loadRates(silent = false): Promise<void> {
  if (!silent) {
    status.value = "loading";
  }

  try {
    const res = await getExchangeRates();
    rates.value = (res.list ?? []).map(normalizeItem);

    if (!silent || status.value !== "success") {
      status.value = rates.value.length ? "success" : "empty";
    }

    if (showModal.value && selected.value) {
      const latest = rates.value.find((item) => item.pair === selected.value?.pair);
      if (latest) {
        selected.value = latest;
      }
    }
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "获取市场数据失败";
    status.value = "error";
  }
}

function startPolling(): void {
  stopPolling();
  refreshTimer = window.setInterval(() => {
    void loadRates(true);
  }, REFRESH_INTERVAL_MS);
}

function stopPolling(): void {
  if (refreshTimer !== null) {
    window.clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

onMounted(() => {
  void loadRates();
  startPolling();
});

onBeforeUnmount(() => {
  stopPolling();
});
</script>

<style scoped>
.market-note {
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.market-note p {
  margin: 6px 0 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.market-note h3 {
  margin: 0;
}

.market-link {
  color: #8ab7ff;
  text-decoration: none;
  white-space: nowrap;
}

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

@media (max-width: 700px) {
  .market-note {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .rate-grid {
    grid-template-columns: 1fr;
  }
}
</style>