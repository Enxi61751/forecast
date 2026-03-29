export interface AgentFeedItem {
  id: string;
  agentName: string;
  role: string;
  direction: string | null;
  riskAttitude: string | null;
  rationale: string | null;
  confidence: number | null;
  memory: string | null;
  remark: string | null;
  updatedAt: string | null;
  tags: string[];
  rawDecisionJson?: Record<string, unknown>;
  parameterCorrection?: Record<string, unknown>;
}

export interface AgentFeedSection {
  id: string;
  title: string;
  items: AgentFeedItem[];
}

export interface AgentPageState {
  asOf: string | null;
  sections: AgentFeedSection[];
  reportTitle: string | null;
  reportBody: string | null;
}

export interface AgentApiResult {
  available: boolean;
  message: string;
  data: AgentPageState | null;
}

export interface SimulationRequest {
  mode: "market_simulation" | "parameter_iteration";
  iterationParams?: Record<string, unknown>;
}

export interface SimulationResponse {
  overallSummary: string;
  agentDecisions: Record<string, Record<string, unknown>>;
  parameterCorrection: Record<string, unknown>;
  agentFeedItems?: AgentFeedItem[];
}
