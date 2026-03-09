import { getMockNews } from "@/mocks";
import type { NewsItem } from "@/types/news";
import { adaptRecentNews, type NewsRecentRawItem } from "./adapters/newsAdapter";
import { requestWithFallback } from "./http";

export async function getRecentNews(days = 7): Promise<NewsItem[]> {
  return requestWithFallback<NewsRecentRawItem[], NewsItem[]>({
    path: `/api/news/recent?days=${encodeURIComponent(String(days))}`,
    mocker: () => getMockNews(),
    mapReal: (rows) => adaptRecentNews(rows)
  });
}
