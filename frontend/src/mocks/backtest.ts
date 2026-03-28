import type { StrategyComparisonRow } from "@/types/backtest";

// Mock data for strategy comparison table
// TODO: replace with API call: GET /api/backtest/comparison
export const mockStrategyComparison: StrategyComparisonRow[] = [
  {
    strategyName: "Aberration+Model(AND)",
    tradeCount: 210,
    winRate: 0.819,
    profitFactor: 13.49,
    maxDrawdown: -5.93,
    oosMaxDrawdown: -1.54
  },
  {
    strategyName: "MACD+Model(VETO)",
    tradeCount: 910,
    winRate: 0.8099,
    profitFactor: 10.52,
    maxDrawdown: -10.98,
    oosMaxDrawdown: -4.1
  },
  {
    strategyName: "DualThrust+Model(VETO)",
    tradeCount: 960,
    winRate: 0.8115,
    profitFactor: 10.41,
    maxDrawdown: -10.94,
    oosMaxDrawdown: -4.1
  },
  {
    strategyName: "Aberration+Model(VETO)",
    tradeCount: 704,
    winRate: 0.8054,
    profitFactor: 10.32,
    maxDrawdown: -7.95,
    oosMaxDrawdown: -4.1
  },
  {
    strategyName: "Momentum+Model(VETO)",
    tradeCount: 458,
    winRate: 0.786,
    profitFactor: 9.53,
    maxDrawdown: -5.59,
    oosMaxDrawdown: -3.28
  },
  {
    strategyName: "Momentum+Model(AND)",
    tradeCount: 447,
    winRate: 0.7808,
    profitFactor: 8.97,
    maxDrawdown: -5.59,
    oosMaxDrawdown: -3.28
  }
];
