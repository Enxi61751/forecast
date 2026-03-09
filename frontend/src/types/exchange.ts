export type ExchangeTimeRange = "1W" | "1M" | "6M";

export interface ExchangeRateCardData {
  id: string;
  pair: string;
  name: string;
  price: number;
  change: number;
  high: number;
  low: number;
  updatedAt: string;
  trend: Record<ExchangeTimeRange, number[]>;
  labels: Record<ExchangeTimeRange, string[]>;
}
