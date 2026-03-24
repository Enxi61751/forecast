import type { BacktestCurvePoint, BacktestMetricItem, BacktestSummary } from "@/types/backtest";

// TODO: align these raw fields with the finalized backtest response schema.
export interface BacktestRawResponse {
  strategyName?: unknown;
  benchmark?: unknown;
  benchmarkName?: unknown;
  period?: unknown;
  notes?: unknown;
  tradeSummary?: unknown;
  periodSummary?: unknown;
  cumulativeReturn?: unknown;
  drawdown?: unknown;
  metrics?: unknown;
}

function toText(value: unknown): string | null {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return null;
}

function toCurve(raw: unknown): BacktestCurvePoint[] {
  if (!Array.isArray(raw)) {
    return [];
  }

  return raw
    .map((item, index) => {
      if (typeof item === "number" && Number.isFinite(item)) {
        return {
          label: `P${index + 1}`,
          value: item
        };
      }

      if (typeof item === "object" && item !== null) {
        const row = item as Record<string, unknown>;
        const numeric = Number(row.value ?? row.return ?? row.drawdown);
        if (!Number.isFinite(numeric)) {
          return null;
        }

        return {
          label: typeof row.label === "string" && row.label.trim() ? row.label : `P${index + 1}`,
          value: numeric
        };
      }

      return null;
    })
    .filter((item): item is BacktestCurvePoint => Boolean(item));
}

function toMetrics(raw: unknown): BacktestMetricItem[] {
  if (!Array.isArray(raw)) {
    return [];
  }

  const metrics: BacktestMetricItem[] = [];

  raw.forEach((item, index) => {
    if (typeof item !== "object" || item === null) {
      return;
    }

    const row = item as Record<string, unknown>;
    const metric: BacktestMetricItem = {
      id: String(row.id ?? `metric-${index}`),
      label: typeof row.label === "string" && row.label.trim() ? row.label : `Metric ${index + 1}`,
      value: typeof row.value === "string" && row.value.trim() ? row.value : String(row.value ?? "--"),
      tone: row.tone === "positive" || row.tone === "negative" ? row.tone : "neutral"
    };

    metrics.push(metric);
  });

  return metrics;
}

export function adaptBacktestSummary(raw: BacktestRawResponse): BacktestSummary {
  return {
    strategyName: toText(raw.strategyName),
    benchmarkName: toText(raw.benchmarkName) ?? toText(raw.benchmark),
    periodLabel: toText(raw.period),
    notes: toText(raw.notes),
    tradeSummary: toText(raw.tradeSummary),
    periodSummary: toText(raw.periodSummary),
    cumulativeReturn: toCurve(raw.cumulativeReturn),
    drawdownCurve: toCurve(raw.drawdown),
    metrics: toMetrics(raw.metrics)
  };
}
