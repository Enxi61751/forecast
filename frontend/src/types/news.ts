export type SentimentLabel = "Positive" | "Neutral" | "Negative";

export interface NewsItem {
  id: string;
  title: string;
  source: string;
  summary: string;
  url: string;
  publishedAt: string;
  sentimentLabel: SentimentLabel;
  sentimentScore: number;
}
