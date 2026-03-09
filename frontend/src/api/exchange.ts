import { getMockExchangeRates } from "@/mocks";
import type { ExchangeRateCardData } from "@/types/exchange";
import { adaptExchangeRates, type ExchangeRawItem } from "./adapters/exchangeAdapter";
import { requestWithFallback } from "./http";

export async function getExchangeRates(): Promise<ExchangeRateCardData[]> {
  return requestWithFallback<ExchangeRawItem[], ExchangeRateCardData[]>({
    path: "/api/exchange/recent",
    mocker: () => getMockExchangeRates(),
    mapReal: (rows) => adaptExchangeRates(rows)
  });
}
