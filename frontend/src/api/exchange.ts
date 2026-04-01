import { requestWithFallback } from "./http";

export interface ExchangeHistoryPoint {
  date: string;
  value: number;
}

export interface ExchangeHistory {
  "1W": ExchangeHistoryPoint[];
  "1M": ExchangeHistoryPoint[];
  "6M": ExchangeHistoryPoint[];
}

export interface ExchangeItem {
  symbol: string;
  name: string;
  date: string;
  open?: number;
  high: number;
  low: number;
  close: number;
  change: number;
  changePercent?: number;
  history: ExchangeHistory;
}

export interface ExchangeListResult {
  list: ExchangeItem[];
  total: number;
}

export function getExchangeRates() {
  return requestWithFallback<ExchangeListResult, ExchangeListResult>({
    path: "/api/data/exchange",
    mocker: async () => {
      throw new Error("实时油价接口不可用，未启用本地 mock 数据");
    }
  });
}