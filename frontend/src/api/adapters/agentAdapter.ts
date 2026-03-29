import type { AgentFeedItem, AgentFeedSection, AgentPageState, SimulationResponse } from "@/types/agent";

// TODO: align these raw fields with the finalized agent daily-report response.
export interface AgentFeedRawItem {
  id?: unknown;
  name?: unknown;
  agentName?: unknown;
  role?: unknown;
  direction?: unknown;
  riskAttitude?: unknown;
  rationale?: unknown;
  confidence?: unknown;
  memory?: unknown;
  note?: unknown;
  remark?: unknown;
  updatedAt?: unknown;
  tags?: unknown;
  rawDecisionJson?: unknown;
  parameterCorrection?: unknown;
}

export interface AgentFeedRawResponse {
  asOf?: unknown;
  reportTitle?: unknown;
  reportBody?: unknown;
  items?: unknown;
  agents?: unknown;
  sections?: unknown;
}

function toText(value: unknown): string | null {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return null;
}

function toConfidence(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function toTags(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map((item) => toText(item)).filter((item): item is string => Boolean(item));
}

function toRecord(value: unknown): Record<string, unknown> | undefined {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return undefined;
  }

  return { ...(value as Record<string, unknown>) };
}

function toDecisionMap(value: unknown): Record<string, Record<string, unknown>> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return {};
  }

  return Object.entries(value as Record<string, unknown>).reduce<Record<string, Record<string, unknown>>>((result, [key, decision]) => {
    const normalizedDecision = toRecord(decision);
    if (normalizedDecision) {
      result[key] = normalizedDecision;
    }
    return result;
  }, {});
}

function mapAgentFeedItem(raw: AgentFeedRawItem, index: number): AgentFeedItem {
  return {
    id: String(raw.id ?? `agent-${index}`),
    agentName: toText(raw.agentName) ?? toText(raw.name) ?? `Agent ${index + 1}`,
    role: toText(raw.role) ?? "Unknown role",
    direction: toText(raw.direction),
    riskAttitude: toText(raw.riskAttitude),
    rationale: toText(raw.rationale),
    confidence: toConfidence(raw.confidence),
    memory: toText(raw.memory),
    remark: toText(raw.remark) ?? toText(raw.note),
    updatedAt: toText(raw.updatedAt),
    tags: toTags(raw.tags),
    rawDecisionJson: toRecord(raw.rawDecisionJson) ?? {},
    parameterCorrection: toRecord(raw.parameterCorrection)
  };
}

function adaptSections(raw: AgentFeedRawResponse): AgentFeedSection[] {
  if (Array.isArray(raw.sections)) {
    return raw.sections
      .map((section, index) => {
        if (typeof section !== "object" || section === null) {
          return null;
        }

        const row = section as Record<string, unknown>;
        const items = Array.isArray(row.items) ? row.items : [];

        return {
          id: String(row.id ?? `section-${index}`),
          title: toText(row.title) ?? `Section ${index + 1}`,
          items: items
            .map((item, itemIndex) => (typeof item === "object" && item !== null ? mapAgentFeedItem(item as AgentFeedRawItem, itemIndex) : null))
            .filter((item): item is AgentFeedItem => Boolean(item))
        };
      })
      .filter((section): section is AgentFeedSection => Boolean(section));
  }

  const source = Array.isArray(raw.items) ? raw.items : Array.isArray(raw.agents) ? raw.agents : [];
  if (!source.length) {
    return [];
  }

  return [
    {
      id: "daily-feed",
      title: "Daily Agent Feed",
      items: source
        .map((item, index) => (typeof item === "object" && item !== null ? mapAgentFeedItem(item as AgentFeedRawItem, index) : null))
        .filter((item): item is AgentFeedItem => Boolean(item))
    }
  ];
}

export function adaptAgentFeed(raw: AgentFeedRawResponse): AgentPageState {
  return {
    asOf: toText(raw.asOf),
    sections: adaptSections(raw),
    reportTitle: toText(raw.reportTitle),
    reportBody: toText(raw.reportBody)
  };
}

export function adaptSimulationResponse(raw: SimulationResponse) {
  return {
    summary: toText(raw.overallSummary) ?? "",
    decisions: toDecisionMap(raw.agentDecisions),
    correctionParams: toRecord(raw.parameterCorrection) ?? {},
    feedItems: (raw.agentFeedItems ?? []).map((item, index) => mapAgentFeedItem(item, index))
  };
}
