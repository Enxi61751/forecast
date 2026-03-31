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
  explanation?: unknown;
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
  // Handle backend format: { point: [{t, v}], lower: [...], upper: [...] }
  if (typeof raw === "object" && raw !== null && !Array.isArray(raw)) {
    const obj = raw as Record<string, unknown>;
    if (Array.isArray(obj.point)) {
      return normalizeSeries(obj.point);
    }
  }

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
          time: toText(row.t ?? row.time ?? row.date ?? row.label, `D+${index + 1}`),
          value: toFiniteNumber(row.v ?? row.value ?? row.price ?? row.prediction)
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
    risk: typeof row.risk === "undefined" || row.risk === null ? null : toText(row.risk, ""),
    confidence: typeof row.confidence === "undefined" || row.confidence === null ? null : toFiniteNumber(row.confidence, 0),
    explanation: typeof row.explanation === "undefined" || row.explanation === null ? null : toText(row.explanation, "")
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
  const rawForecast = raw.forecast ?? ((raw as Record<string, unknown>).result ?? null);

  // Extract lower/upper from forecast object if present (backend format: {point, lower, upper})
  let rawLower: unknown = raw.lowerBound;
  let rawUpper: unknown = raw.upperBound;
  if (typeof rawForecast === "object" && rawForecast !== null && !Array.isArray(rawForecast)) {
    const forecastObj = rawForecast as Record<string, unknown>;
    if (!rawLower && forecastObj.lower) rawLower = forecastObj.lower;
    if (!rawUpper && forecastObj.upper) rawUpper = forecastObj.upper;
  }

  const forecast = normalizeSeries(rawForecast);
  const fallbackForecast = forecast.length
    ? forecast
    : [{ time: "D+1", value: 0 }];

  const summary = adaptSummary(raw.summary);
  const explainText = typeof raw.explain === "string" && raw.explain.trim() ? raw.explain : summary.explanation;
  const nextDayPoint = fallbackForecast[0] ?? null;

  return {
    runId: String(raw.runId ?? `real-run-${Date.now()}`),
    target: toText(raw.target, req.target),
    horizon: toText(raw.horizon, req.horizon),
    forecast: fallbackForecast,
    lowerBound: withFallbackBand(fallbackForecast, rawLower, 0.992),
    upperBound: withFallbackBand(fallbackForecast, rawUpper, 1.008),
    nextDayPoint,
    summary,
    reportPreview: explainText ?? null,
    generatedAt: toText(raw.generatedAt, new Date().toISOString())
  };
}
