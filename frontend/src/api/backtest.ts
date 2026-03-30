import type {
  BacktestApiResult,
  BacktestCurvePoint,
  BacktestMetricItem
} from "@/types/backtest";
import { requestWithFallback } from "./http";

export interface BacktestRunParams {
  symbol: string;
  startDate: string;
  endDate: string;
  strategies: string[];
  combineModes: string[];
  feeSlipRatePerSide: number;
}

interface BackendBacktestDataInfo {
  symbol?: string;
  totalBars?: number;
  dataStartDate?: string | null;
  dataEndDate?: string | null;
  mlPredictionsAvailable?: boolean;
  mlPredictionCount?: number;
  overlappingBars?: number;
  note?: string | null;
}

interface BackendEquityPoint {
  date?: string;
  equity?: number;
}

interface BackendStrategyBacktestResult {
  strategyName?: string;
  strategy_name?: string;

  nTrades?: number;
  winRate?: number;
  win_rate?: number;

  totalReturn?: number;
  total_return?: number;

  maxDrawdown?: number;
  max_drawdown?: number;

  avgReturnPerTrade?: number;
  avg_return_per_trade?: number;

  avgWin?: number;
  avg_win?: number;

  avgLoss?: number;
  avg_loss?: number;

  profitFactor?: number;
  profit_factor?: number;

  oosReturn?: number;
  oos_return?: number;

  oosWinRate?: number;
  oos_win_rate?: number;

  oosMaxDrawdown?: number;
  oos_max_drawdown?: number;

  worstRollingDrawdown63d?: number;
  worst_rolling_drawdown63d?: number;

  equityCurve?: BackendEquityPoint[];
  equity_curve?: BackendEquityPoint[];
}

interface BackendBacktestResponse {
  dataInfo?: BackendBacktestDataInfo | null;
  results?: BackendStrategyBacktestResult[] | null;
}

const DEFAULT_BACKTEST_REQUEST: BacktestRunParams = {
  symbol: "LCO1",
  startDate: "2022-01-01",
  endDate: "2024-12-31",
  strategies: ["MACD"],
  combineModes: ["baseOnly"],
  feeSlipRatePerSide: 0.0005
};

function isValidNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function formatPercent(value: unknown, digits = 2): string {
  if (!isValidNumber(value)) return "--";
  return `${(value * 100).toFixed(digits)}%`;
}

function formatNumber(value: unknown, digits = 2): string {
  if (!isValidNumber(value)) return "--";
  return value.toFixed(digits);
}

function buildCumulativeReturnCurve(
  equityCurve: BackendEquityPoint[]
): BacktestCurvePoint[] {
  return equityCurve
    .filter((point) => point.date && isValidNumber(point.equity))
    .map((point) => ({
      label: point.date as string,
      value: Number(((point.equity as number) - 1).toFixed(4))
    }));
}

function buildDrawdownCurve(
  equityCurve: BackendEquityPoint[]
): BacktestCurvePoint[] {
  let runningPeak = 0;

  return equityCurve
    .filter((point) => point.date && isValidNumber(point.equity))
    .map((point) => {
      const equity = point.equity as number;
      runningPeak = Math.max(runningPeak, equity);
      const drawdown = runningPeak > 0 ? equity / runningPeak - 1 : 0;

      return {
        label: point.date as string,
        value: Number(drawdown.toFixed(4))
      };
    });
}

function buildMetrics(result: BackendStrategyBacktestResult): BacktestMetricItem[] {
  const winRate = result.winRate ?? result.win_rate;
  const profitFactor = result.profitFactor ?? result.profit_factor;
  const totalReturn = result.totalReturn ?? result.total_return;
  const maxDrawdown = result.maxDrawdown ?? result.max_drawdown;

  return [
    {
      id: "win-rate",
      label: "Win Rate",
      value: formatPercent(winRate),
      tone:
        isValidNumber(winRate) && winRate >= 0.5
          ? "positive"
          : "negative"
    },
    {
      id: "profit-factor",
      label: "Profit Factor",
      value: formatNumber(profitFactor),
      tone:
        isValidNumber(profitFactor) && profitFactor >= 1
          ? "positive"
          : "negative"
    },
    {
      id: "total-return",
      label: "Total Return",
      value: formatPercent(totalReturn),
      tone:
        isValidNumber(totalReturn) && totalReturn >= 0
          ? "positive"
          : "negative"
    },
    {
      id: "max-drawdown",
      label: "Max Drawdown",
      value: formatPercent(maxDrawdown),
      tone: "negative"
    }
  ];
}

function resolveBenchmarkName(symbol?: string): string {
  const normalized = (symbol || "").toUpperCase();

  if (normalized.includes("WTI") || normalized.startsWith("CL")) {
    return "WTI Crude Oil";
  }
  if (normalized === "LCO1" || normalized.includes("BRENT")) {
    return "Brent Crude Oil";
  }
  return symbol || "Crude Oil";
}

function mapRealBacktestToSummary(real: BackendBacktestResponse): BacktestApiResult {
  const dataInfo = real.dataInfo ?? null;
  const results = real.results ?? [];

  if (!results.length) {
    return {
      available: false,
      message: dataInfo?.note || "后端未返回可展示的策略结果",
      data: null
    };
  }

  const selected = results[0];

  const equityCurve = selected.equityCurve ?? selected.equity_curve ?? [];
  

  return {
    available: true,
    message: "ok",
    data: {
      strategyName: selected.strategyName || "Backtest Strategy",
      benchmarkName: resolveBenchmarkName(dataInfo?.symbol),
      periodLabel:
        dataInfo?.dataStartDate && dataInfo?.dataEndDate
          ? `${dataInfo.dataStartDate} to ${dataInfo.dataEndDate}`
          : null,
      notes: dataInfo?.note || null,
      tradeSummary: `Total ${selected.nTrades ?? 0} trades executed`,
      periodSummary: `${equityCurve.length} bars backtested`,
      cumulativeReturn: buildCumulativeReturnCurve(equityCurve),
      drawdownCurve: buildDrawdownCurve(equityCurve),
      metrics: buildMetrics(selected)
    }
  };
}

function buildMockResult(): BacktestApiResult {
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
        { label: "2020-06", value: 0.05 }
      ],
      drawdownCurve: [
        { label: "2020-01", value: 0 },
        { label: "2020-06", value: -0.03 }
      ],
      metrics: [
        { id: "win-rate", label: "Win Rate", value: "81.90%", tone: "positive" },
        { id: "profit-factor", label: "Profit Factor", value: "13.49", tone: "positive" },
        { id: "max-drawdown", label: "Max Drawdown", value: "-5.93%", tone: "negative" },
        { id: "total-return", label: "Total Return", value: "62.00%", tone: "positive" }
      ]
    }
  };
}

export async function getBacktestSummary(
  params: Partial<BacktestRunParams> = {}
): Promise<BacktestApiResult> {
  const payload: BacktestRunParams = {
    ...DEFAULT_BACKTEST_REQUEST,
    ...params
  };

  return requestWithFallback<BackendBacktestResponse, BacktestApiResult>({
    path: "/api/backtest/run",
    init: {
      method: "POST",
      body: JSON.stringify(payload)
    },
    mocker: buildMockResult,
    mapReal: mapRealBacktestToSummary
  });
}