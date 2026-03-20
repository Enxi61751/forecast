import { requestWithFallback } from "./http";
import type { NewsItem } from "@/types/news";

export interface NewsListResult {
  list: NewsItem[];
  total: number;
}

export function getNewsList() {
  return requestWithFallback<NewsListResult, NewsListResult>({
    path: "/api/news/list",
    mocker: async () => ({
      total: 2,
      list: [
        {
          id: "1",
          title: "Mock News 1",
          source: "Mock Source",
          summary: "This is a mock news summary.",
          url: "https://example.com/news/1",
          publishedAt: new Date().toISOString(),
          sentimentLabel: "Positive",
          sentimentScore: 0.82
        },
        {
          id: "2",
          title: "Mock News 2",
          source: "Mock Source",
          summary: "This is another mock news summary.",
          url: "https://example.com/news/2",
          publishedAt: new Date().toISOString(),
          sentimentLabel: "Neutral",
          sentimentScore: 0.56
        }
      ]
    })
  });
}