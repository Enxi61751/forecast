import type { NewsItem } from "@/types/news";

export const mockNews: NewsItem[] = [
  {
    id: "n1",
    title: "国际能源组织上调短期需求预期",
    source: "Reuters",
    summary: "需求预期上调带动风险资产情绪修复，价格波动预期略有抬升。",
    url: "https://example.com/news/1",
    publishedAt: "2026-03-09T06:30:00Z",
    sentimentLabel: "Positive",
    sentimentScore: 0.74
  },
  {
    id: "n2",
    title: "主要经济体公布最新通胀数据",
    source: "Bloomberg",
    summary: "通胀压力高于预期，市场对后续政策路径分歧扩大。",
    url: "https://example.com/news/2",
    publishedAt: "2026-03-08T12:00:00Z",
    sentimentLabel: "Neutral",
    sentimentScore: 0.51
  },
  {
    id: "n3",
    title: "区域供应链扰动引发避险情绪",
    source: "WSJ",
    summary: "避险资金流动上升，短时波动可能显著放大。",
    url: "https://example.com/news/3",
    publishedAt: "2026-03-07T08:00:00Z",
    sentimentLabel: "Negative",
    sentimentScore: 0.22
  }
];

export async function getMockNews(): Promise<NewsItem[]> {
  await new Promise((resolve) => setTimeout(resolve, 420));
  return mockNews;
}
