import type { BacktestApiResult } from "@/types/backtest";

export async function getBacktestSummary(): Promise<BacktestApiResult> {
  // TODO: replace with real API call when backend is ready
  return {
    available: true,
    message: "Mock data for development",
    data: {
      strategyName: "CEEMDAN-LightGBM-TFT",
      benchmarkName: "WTI Crude Oil",
      periodLabel: "2020-01 to 2025-12",
      notes: "Model ensemble strategy with CEEMDAN decomposition",
      tradeSummary: "Total 210 trades executed",
      periodSummary: "72 months backtested",
      cumulativeReturn: [
        { label: "2020-01", value: 0 },
        { label: "2020-06", value: 0.05 },
        { label: "2021-01", value: 0.12 },
        { label: "2021-06", value: 0.18 },
        { label: "2022-01", value: 0.25 },
        { label: "2022-06", value: 0.32 },
        { label: "2023-01", value: 0.28 },
        { label: "2023-06", value: 0.35 },
        { label: "2024-01", value: 0.42 },
        { label: "2024-06", value: 0.48 },
        { label: "2025-01", value: 0.55 },
        { label: "2025-06", value: 0.62 }
      ],
      drawdownCurve: [
        { label: "2020-01", value: 0 },
        { label: "2020-06", value: -0.03 },
        { label: "2021-01", value: -0.02 },
        { label: "2021-06", value: -0.05 },
        { label: "2022-01", value: -0.04 },
        { label: "2022-06", value: -0.08 },
        { label: "2023-01", value: -0.1 },
        { label: "2023-06", value: -0.06 },
        { label: "2024-01", value: -0.04 },
        { label: "2024-06", value: -0.03 },
        { label: "2025-01", value: -0.02 },
        { label: "2025-06", value: -0.01 }
      ],
      metrics: [
        { id: "win-rate", label: "Win Rate", value: "81.90%", tone: "positive" },
        { id: "profit-factor", label: "Profit Factor", value: "13.49", tone: "positive" },
        { id: "max-drawdown", label: "Max Drawdown", value: "-5.93%", tone: "negative" },
        { id: "sharpe", label: "Sharpe Ratio", value: "2.15", tone: "positive" }
      ]
    }
  };
}
