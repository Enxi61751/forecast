import type { NewsItem, SentimentLabel } from "@/types/news";

// TODO: align these raw fields with finalized /api/news/recent response.
export interface NewsRecentRawItem {
  id?: string | number;
  title?: unknown;
  source?: unknown;
  summary?: unknown;
  content?: unknown;
  url?: unknown;
  publishedAt?: unknown;
  sentiment?: unknown;
  sentimentScore?: unknown;
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

function sentimentLabelByScore(score: number): SentimentLabel {
  if (score >= 0.67) return "Positive";
  if (score <= 0.33) return "Negative";
  return "Neutral";
}

export function adaptRecentNews(rows: NewsRecentRawItem[]): NewsItem[] {
  return rows.map((row, index) => {
    const sentimentScore = toFiniteNumber(row.sentiment, toFiniteNumber(row.sentimentScore, 0.5));

    return {
      id: String(row.id ?? `news-${index}`),
      title: toText(row.title, "Untitled News"),
      source: toText(row.source, "unknown"),
      summary: toText(row.summary, toText(row.content, "Summary is unavailable.")),
      url: toText(row.url, "#"),
      publishedAt: toText(row.publishedAt, new Date().toISOString()),
      sentimentLabel: sentimentLabelByScore(sentimentScore),
      sentimentScore
    };
  });
}
