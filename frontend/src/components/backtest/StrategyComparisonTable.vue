<template>
  <section class="card comparison-table-wrapper">
    <header class="comparison-header">
      <h3>收益概述</h3>
    </header>
    <div class="table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>策略</th>
            <th>交易笔数</th>
            <th>胜率</th>
            <th>盈亏因子</th>
            <th>最大回撤(%)</th>
            <th>样本外最大回撤(%)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.strategyName">
            <td>{{ row.strategyName }}</td>
            <td>{{ row.tradeCount }}</td>
            <td>{{ formatPercent(row.winRate) }}</td>
            <td>{{ row.profitFactor.toFixed(2) }}</td>
            <td class="negative">{{ row.maxDrawdown.toFixed(2) }}</td>
            <td class="negative">{{ row.oosMaxDrawdown.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { StrategyComparisonRow } from "@/types/backtest";

defineProps<{
  rows: StrategyComparisonRow[];
}>();

function formatPercent(value: number): string {
  return (value * 100).toFixed(2) + "%";
}
</script>

<style scoped>
.comparison-table-wrapper {
  margin-top: 1.5rem;
}

.comparison-header {
  margin-bottom: 1rem;
}

.comparison-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.table-scroll {
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.comparison-table th,
.comparison-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.comparison-table th {
  font-weight: 600;
  color: var(--color-text-secondary);
  background: rgba(255, 255, 255, 0.04);
}

.comparison-table td {
  color: var(--color-text-primary);
}

.comparison-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.03);
}

.comparison-table td.negative {
  color: var(--color-negative);
}
</style>
