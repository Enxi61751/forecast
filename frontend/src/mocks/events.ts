import type { EventItem } from "@/types/events";

export const mockEvents: EventItem[] = [
  {
    id: "e1",
    eventType: "GeoPoliticalShock",
    summary: "中东地区运输通道风险升温，市场波动偏好下降。",
    intensity: 0.86,
    occurredAt: "2026-03-08T20:00:00Z"
  },
  {
    id: "e2",
    eventType: "PolicySignal",
    summary: "主要央行释放偏鹰派信号，利率路径预期抬升。",
    intensity: 0.68,
    occurredAt: "2026-03-07T09:00:00Z"
  },
  {
    id: "e3",
    eventType: "InventorySurprise",
    summary: "库存数据低于预期，引发能源价格快速回补。",
    intensity: 0.73,
    occurredAt: "2026-03-06T14:30:00Z"
  }
];

export async function getMockEvents(): Promise<EventItem[]> {
  await new Promise((resolve) => setTimeout(resolve, 420));
  return mockEvents;
}
