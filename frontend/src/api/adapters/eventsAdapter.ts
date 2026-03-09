import type { EventItem } from "@/types/events";

// TODO: align these raw fields with finalized /api/events/recent response.
export interface EventsRecentRawItem {
  id?: string | number;
  eventType?: unknown;
  summary?: unknown;
  intensity?: unknown;
  occurredAt?: unknown;
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

export function adaptRecentEvents(rows: EventsRecentRawItem[]): EventItem[] {
  return rows.map((row, index) => ({
    id: String(row.id ?? `event-${index}`),
    eventType: toText(row.eventType, "Unknown"),
    summary: toText(row.summary, "No summary available."),
    intensity: toFiniteNumber(row.intensity),
    occurredAt: toText(row.occurredAt, new Date().toISOString())
  }));
}
