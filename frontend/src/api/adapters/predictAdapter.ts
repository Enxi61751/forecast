import type { PredictionPoint, PredictionResult, PredictionRunRequest } from "@/types/predict";

// TODO: align these raw fields with finalized FastAPI response schema.
export interface PredictRunRawResponse {
  runId?: string | number;
  target?: string;
  horizon?: string;
  forecast?: unknown;
  lowerBound?: unknown;
  upperBound?: unknown;
  summary?: unknown;
  explain?: unknown;
  generatedAt?: unknown;
}

export interface PredictLatestRawResponse extends PredictRunRawResponse {}

interface PredictionSummaryRaw {
  trend?: unknown;
  risk?: unknown;
  confidence?: unknown;
}

function toFiniteNumber(value: unknown, fallback = 0): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function toText(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

function normalizeSeries(raw: unknown): PredictionPoint[] {
  if (!Array.isArray(raw)) {
    return [];
  }

  return raw
    .map((item, index) => {
      if (typeof item === "number") {
        return { time: `D+${index + 1}`, value: item };
      }

      if (typeof item === "object" && item !== null) {
        const row = item as Record<string, unknown>;
        return {
          time: toText(row.time, `D+${index + 1}`),
          value: toFiniteNumber(row.value)
        };
      }

      return {
        time: `D+${index + 1}`,
        value: 0
      };
    })
    .filter((point) => Number.isFinite(point.value));
}

function adaptSummary(raw: unknown): PredictionResult["summary"] {
  const row = (typeof raw === "object" && raw !== null ? raw : {}) as PredictionSummaryRaw;

  return {
    trend: toText(row.trend, "Trend pending backend final schema"),
    risk: toText(row.risk, "Risk description pending backend final schema"),
    confidence: toFiniteNumber(row.confidence, 0.8)
  };
}

function withFallbackBand(forecast: PredictionPoint[], band: unknown, ratio: number): PredictionPoint[] {
  const rawBand = normalizeSeries(band);
  if (rawBand.length) {
    return rawBand;
  }

  return forecast.map((point) => ({
    time: point.time,
    value: Number((point.value * ratio).toFixed(4))
  }));
}

export function adaptPredictionResult(raw: PredictRunRawResponse, req: PredictionRunRequest): PredictionResult {
  const forecast = normalizeSeries(raw.forecast);
  const fallbackForecast = forecast.length
    ? forecast
    : [
        { time: "D+1", value: 0 },
        { time: "D+2", value: 0 }
      ];

  const summary = adaptSummary(raw.summary);
  const explainText = typeof raw.explain === "string" ? raw.explain : "Explanation is pending backend final schema.";

  return {
    runId: String(raw.runId ?? `real-run-${Date.now()}`),
    target: toText(raw.target, req.target),
    horizon: toText(raw.horizon, req.horizon),
    forecast: fallbackForecast,
    lowerBound: withFallbackBand(fallbackForecast, raw.lowerBound, 0.992),
    upperBound: withFallbackBand(fallbackForecast, raw.upperBound, 1.008),
    summary,
    reportPreview: explainText,
    generatedAt: toText(raw.generatedAt, new Date().toISOString())
  };
}
