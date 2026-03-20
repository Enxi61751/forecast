import { requestWithFallback } from "./http";
import type { EventItem } from "@/types/events";

export interface EventListResult {
  list: EventItem[];
  total: number;
}

export function getEventList() {
  return requestWithFallback<EventListResult, EventListResult>({
    path: "/api/data/events",
    mocker: async () => ({
      total: 2,
      list: [
        {
          id: "1",
          title: "Mock Event A",
          eventType: "policy",
          summary: "A mock policy-related event happened.",
          intensity: 0.75,
          occurredAt: new Date().toISOString()
        },
        {
          id: "2",
          title: "Mock Event B",
          eventType: "market",
          summary: "A mock market-related event happened.",
          intensity: 0.61,
          occurredAt: new Date().toISOString()
        }
      ]
    })
  });
}