import { requestWithFallback } from "./http";

export interface ExchangeItem {
  date: string;
  rate: number;
}

export interface ExchangeListResult {
  list: ExchangeItem[];
  total: number;
}

export function getExchangeList() {
  return requestWithFallback<ExchangeListResult, ExchangeListResult>({
    path: "/api/data/exchange",
    mocker: async () => ({
      total: 2,
      list: [
        { date: "2026-03-18", rate: 7.21 },
        { date: "2026-03-19", rate: 7.23 }
      ]
    })
  });
}