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
