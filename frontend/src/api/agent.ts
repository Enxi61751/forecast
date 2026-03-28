import type { AgentApiResult, AgentPageState } from "@/types/agent";
import { requestWithFallback } from "./http";
import { adaptAgentFeed, type AgentFeedRawResponse } from "./adapters/agentAdapter";
import { getMockAgentFeed } from "@/mocks";

const AGENT_BASE_URL = import.meta.env.VITE_AGENT_BASE_URL || "http://localhost:8001";

export async function getAgentFeed(): Promise<AgentApiResult> {
  try {
    const result = await requestWithFallback<AgentFeedRawResponse, AgentPageState>({
      path: `${AGENT_BASE_URL}/agent/daily-feed`,
      init: {
        method: "GET"
      },
      mocker: async () => {
        const raw = await getMockAgentFeed();
        return adaptAgentFeed(raw);
      },
      mapReal: (raw) => adaptAgentFeed(raw)
    });

    return {
      available: true,
      message: "Success from real agent service",
      data: result
    };
  } catch (error) {
    console.error("Failed to fetch agent feed:", error);
    return {
      available: false,
      message: error instanceof Error ? error.message : "Failed to fetch agent feed",
      data: null
    };
  }
}