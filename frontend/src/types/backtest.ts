export interface BacktestCurvePoint {
  label: string;
  value: number;
}

export interface BacktestMetricItem {
  id: string;
  label: string;
  value: string;
  tone?: "neutral" | "positive" | "negative";
}

export interface BacktestSummary {
  strategyName: string | null;
  benchmarkName: string | null;
  periodLabel: string | null;
  notes: string | null;
  tradeSummary: string | null;
  periodSummary: string | null;
  cumulativeReturn: BacktestCurvePoint[];
  drawdownCurve: BacktestCurvePoint[];
  metrics: BacktestMetricItem[];
}

export interface BacktestApiResult {
  available: boolean;
  message: string;
  data: BacktestSummary | null;
}

// Strategy comparison table row
export interface StrategyComparisonRow {
  strategyName: string;
  tradeCount: number;
  winRate: number;
  profitFactor: number;
  maxDrawdown: number;
  oosMaxDrawdown: number;
}
