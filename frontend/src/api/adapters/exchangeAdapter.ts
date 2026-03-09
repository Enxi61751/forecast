import type { ExchangeRateCardData, ExchangeTimeRange } from "@/types/exchange";

// TODO: align exchange raw shape once backend exchange endpoint is finalized.
export interface ExchangeRawItem {
  id?: unknown;
  pair?: unknown;
  name?: unknown;
  price?: unknown;
  change?: unknown;
  high?: unknown;
  low?: unknown;
  updatedAt?: unknown;
  trend?: unknown;
  labels?: unknown;
}

function toText(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

function toFiniteNumber(value: unknown, fallback = 0): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function createFallbackTrend(price: number): Record<ExchangeTimeRange, number[]> {
  return {
    "1W": [price * 0.992, price * 0.994, price * 0.996, price * 0.998, price, price * 1.002, price * 1.004].map((x) =>
      Number(x.toFixed(4))
    ),
    "1M": [price * 0.988, price * 0.992, price * 0.997, price, price * 1.003, price * 1.005, price * 1.007, price].map((x) =>
      Number(x.toFixed(4))
    ),
    "6M": [price * 0.96, price * 0.97, price * 0.98, price * 0.99, price, price * 1.01, price * 1.02, price * 1.03].map((x) =>
      Number(x.toFixed(4))
    )
  };
}

function createFallbackLabels(): Record<ExchangeTimeRange, string[]> {
  return {
    "1W": ["D1", "D2", "D3", "D4", "D5", "D6", "D7"],
    "1M": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
    "6M": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"]
  };
}

function normalizeSeriesMap(raw: unknown, fallback: Record<ExchangeTimeRange, number[]>): Record<ExchangeTimeRange, number[]> {
  if (typeof raw !== "object" || raw === null) {
    return fallback;
  }
  const value = raw as Record<string, unknown>;

  const convert = (key: ExchangeTimeRange): number[] => {
    if (!Array.isArray(value[key])) {
      return fallback[key];
    }
    const series = value[key] as unknown[];
    const normalized = series.map((item) => toFiniteNumber(item)).filter((num) => Number.isFinite(num));
    return normalized.length ? normalized : fallback[key];
  };

  return {
    "1W": convert("1W"),
    "1M": convert("1M"),
    "6M": convert("6M")
  };
}

function normalizeLabelMap(raw: unknown, fallback: Record<ExchangeTimeRange, string[]>): Record<ExchangeTimeRange, string[]> {
  if (typeof raw !== "object" || raw === null) {
    return fallback;
  }
  const value = raw as Record<string, unknown>;

  const convert = (key: ExchangeTimeRange): string[] => {
    if (!Array.isArray(value[key])) {
      return fallback[key];
    }
    const labels = (value[key] as unknown[]).map((item) => toText(item, "")).filter(Boolean);
    return labels.length ? labels : fallback[key];
  };

  return {
    "1W": convert("1W"),
    "1M": convert("1M"),
    "6M": convert("6M")
  };
}

export function adaptExchangeRates(rawItems: ExchangeRawItem[]): ExchangeRateCardData[] {
  return rawItems.map((raw, index) => {
    const price = toFiniteNumber(raw.price, 0);
    const fallbackTrend = createFallbackTrend(price);
    const fallbackLabels = createFallbackLabels();

    return {
      id: toText(raw.id, `exchange-${index}`),
      pair: toText(raw.pair, `PAIR-${index}`),
      name: toText(raw.name, "Unknown Pair"),
      price,
      change: toFiniteNumber(raw.change),
      high: toFiniteNumber(raw.high, price),
      low: toFiniteNumber(raw.low, price),
      updatedAt: toText(raw.updatedAt, new Date().toISOString()),
      trend: normalizeSeriesMap(raw.trend, fallbackTrend),
      labels: normalizeLabelMap(raw.labels, fallbackLabels)
    };
  });
}
