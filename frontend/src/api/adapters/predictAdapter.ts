import type { PredictionPoint, PredictionResult, PredictionRunRequest } from "@/types/predict";

export interface PredictRunRawResponse {
  runId?: string | number;
  run_id?: string | number;
  target?: string;
  horizon?: string;
  forecast?: unknown;
  lowerBound?: unknown;
  lower_bound?: unknown;
  upperBound?: unknown;
  upper_bound?: unknown;
  summary?: unknown;
  explain?: unknown;
  extremeClass?: unknown;
  extreme_class?: unknown;
  generatedAt?: unknown;
  generated_at?: unknown;
}

export interface PredictLatestRawResponse extends PredictRunRawResponse {}

interface ApiEnvelope<T> {
  code?: number;
  message?: string;
  data?: T;
}

interface PredictionSummaryRaw {
  trend?: unknown;
  risk?: unknown;
  confidence?: unknown;
  explanation?: unknown;
}

function unwrapApiResponse<T>(payload: ApiEnvelope<T> | T): T {
  if (
    payload &&
    typeof payload === "object" &&
    "data" in payload
  ) {
    return (payload as ApiEnvelope<T>).data as T;
  }
  return payload as T;
}

function toFiniteNumber(value: unknown, fallback = 0): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function toNullableFiniteNumber(value: unknown): number | null {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function toText(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

function normalizeSeries(raw: unknown): PredictionPoint[] {
  if (typeof raw === "object" && raw !== null && !Array.isArray(raw)) {
    const obj = raw as Record<string, unknown>;
    if (Array.isArray(obj.point)) {
      return normalizeSeries(obj.point);
    }
    if (Array.isArray(obj.predictions)) {
      return normalizeSeries(obj.predictions);
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

function extractExtreme(raw: unknown): {
  label: string | null;
  prob: number | null;
} {
  if (typeof raw !== "object" || raw === null) {
    return { label: null, prob: null };
  }

  const obj = raw as Record<string, unknown>;

  const label =
    typeof obj.label === "string"
      ? obj.label
      : typeof obj.class === "string"
        ? obj.class
        : null;

  const prob = toNullableFiniteNumber(
    obj.prob ?? obj.confidence ?? obj.probability
  );

  return { label, prob };
}

function buildTrendText(
  forecast: PredictionPoint[],
  req: PredictionRunRequest
): string {
  if (!forecast.length) {
    return `${req.target} prediction available`;
  }

  const first = forecast[0]?.value ?? 0;
  const last = forecast[forecast.length - 1]?.value ?? first;
  const diff = last - first;

  if (Math.abs(diff) < 1e-8) {
    return `${req.target} remains range-bound`;
  }
  if (diff > 0) {
    return `${req.target} shows an upward bias`;
  }
  return `${req.target} shows a downward bias`;
}

function buildRiskText(label: string | null, prob: number | null): string | null {
  if (!label && prob == null) {
    return null;
  }

  if (label && prob != null) {
    return `${label} (${(prob * 100).toFixed(1)}%)`;
  }

  if (label) {
    return label;
  }

  return prob == null ? null : `Risk probability ${(prob * 100).toFixed(1)}%`;
}

function buildExplanationText(rawExplain: unknown, forecast: PredictionPoint[]): string | null {
  if (typeof rawExplain === "string" && rawExplain.trim()) {
    return rawExplain;
  }

  if (typeof rawExplain === "object" && rawExplain !== null) {
    const obj = rawExplain as Record<string, unknown>;
    if (typeof obj.notes === "string" && obj.notes.trim()) {
      return obj.notes;
    }

    if (typeof obj.model_outputs === "object" && obj.model_outputs !== null) {
      const outputs = obj.model_outputs as Record<string, unknown>;
      const pieces: string[] = [];

      if (outputs.lgbm != null) {
        pieces.push(`LGBM=${Number(outputs.lgbm).toFixed(4)}`);
      }
      if (outputs.tft != null) {
        pieces.push(`TFT=${Number(outputs.tft).toFixed(4)}`);
      }
      if (outputs.ensemble != null) {
        pieces.push(`Ensemble=${Number(outputs.ensemble).toFixed(4)}`);
      }

      if (pieces.length) {
        return `Model outputs: ${pieces.join(", ")}`;
      }
    }
  }

  if (forecast.length) {
    return `The backend returned ${forecast.length} forecast point(s).`;
  }

  return null;
}

function adaptSummary(
  rawSummary: unknown,
  extremeRaw: unknown,
  rawExplain: unknown,
  forecast: PredictionPoint[],
  req: PredictionRunRequest
): PredictionResult["summary"] {
  const row = (typeof rawSummary === "object" && rawSummary !== null ? rawSummary : {}) as PredictionSummaryRaw;
  const extreme = extractExtreme(extremeRaw);

  const trend =
    typeof row.trend === "string" && row.trend.trim()
      ? row.trend
      : buildTrendText(forecast, req);

  const risk =
    typeof row.risk === "string" && row.risk.trim()
      ? row.risk
      : buildRiskText(extreme.label, extreme.prob);

  const confidence =
    typeof row.confidence !== "undefined" && row.confidence !== null
      ? toFiniteNumber(row.confidence, 0)
      : extreme.prob;

  const explanation =
    typeof row.explanation === "string" && row.explanation.trim()
      ? row.explanation
      : buildExplanationText(rawExplain, forecast);

  return {
    trend,
    risk: risk ?? null,
    confidence: confidence ?? null,
    explanation: explanation ?? null
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

export function adaptPredictionResult(
  rawPayload: PredictRunRawResponse,
  req: PredictionRunRequest
): PredictionResult {
  const raw = unwrapApiResponse<PredictRunRawResponse>(rawPayload);

  const rawForecast = raw?.forecast ?? ((raw as Record<string, unknown>)?.result ?? null);

  let rawLower: unknown = raw?.lowerBound ?? raw?.lower_bound;
  let rawUpper: unknown = raw?.upperBound ?? raw?.upper_bound;

  if (typeof rawForecast === "object" && rawForecast !== null && !Array.isArray(rawForecast)) {
    const forecastObj = rawForecast as Record<string, unknown>;
    if (!rawLower && forecastObj.lower) {
      rawLower = forecastObj.lower;
    }
    if (!rawUpper && forecastObj.upper) {
      rawUpper = forecastObj.upper;
    }
  }

  const forecast = normalizeSeries(rawForecast);
  const fallbackForecast = forecast.length
    ? forecast
    : [{ time: "D+1", value: 0 }];

  const summary = adaptSummary(
    raw?.summary,
    raw?.extremeClass ?? raw?.extreme_class,
    raw?.explain,
    fallbackForecast,
    req
  );

  const explainText =
    typeof raw?.explain === "string" && raw.explain.trim()
      ? raw.explain
      : summary.explanation;

  const nextDayPoint = fallbackForecast[0] ?? null;

  return {
    runId: String(raw?.runId ?? raw?.run_id ?? `real-run-${Date.now()}`),
    target: toText(raw?.target, req.target),
    horizon: toText(raw?.horizon, req.horizon),
    forecast: fallbackForecast,
    lowerBound: withFallbackBand(fallbackForecast, rawLower, 0.992),
    upperBound: withFallbackBand(fallbackForecast, rawUpper, 1.008),
    nextDayPoint,
    summary,
    reportPreview: explainText ?? null,
    generatedAt: toText(raw?.generatedAt ?? raw?.generated_at, new Date().toISOString())
  };
}