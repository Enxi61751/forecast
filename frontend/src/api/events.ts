import { getMockEvents } from "@/mocks";
import type { EventItem } from "@/types/events";
import { adaptRecentEvents, type EventsRecentRawItem } from "./adapters/eventsAdapter";
import { requestWithFallback } from "./http";

export async function getRecentEvents(): Promise<EventItem[]> {
  return requestWithFallback<EventsRecentRawItem[], EventItem[]>({
    path: "/api/events/recent",
    mocker: () => getMockEvents(),
    mapReal: (rows) => adaptRecentEvents(rows)
  });
}
