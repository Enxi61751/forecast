import type { AgentApiResult, AgentPageState, SimulationRequest, SimulationResponse } from "@/types/agent";
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

async function getMockSimulationResponse(): Promise<SimulationResponse> {
  await new Promise((resolve) => setTimeout(resolve, 700));
  return MOCK_SIMULATION_RESPONSE;
}

async function requestSimulation(payload: SimulationRequest, path: string): Promise<SimulationResponse> {
  return requestWithFallback<SimulationResponse, SimulationResponse>({
    path,
    init: {
      method: "POST",
      body: JSON.stringify(payload)
    },
    mocker: getMockSimulationResponse
  });
}

export async function simulateMarket(): Promise<SimulationResponse> {
  // TODO: connect to real backend endpoint.
  // For now return mock data so the page renders.
  return requestSimulation({ mode: "market_simulation" }, "/api/agent/simulate");
}

export async function iterateWithParams(params: Record<string, unknown>): Promise<SimulationResponse> {
  // TODO: connect to real backend endpoint.
  // For now return mock data so the page renders.
  return requestSimulation(
    {
      mode: "parameter_iteration",
      iterationParams: params
    },
    "/api/agent/iterate"
  );
}

const MOCK_SIMULATION_RESPONSE: SimulationResponse = {
  overallSummary: "当前市场处于震荡偏强阶段，CTA 与宏观配置建议保留顺势多头，但需要通过更高的对冲比例和更紧的止损控制回撤。",
  agentDecisions: {
    CTA: {
      signal: "long",
      confidence: 0.78,
      targetPriceRange: [70.8, 74.2],
      recommendedLeverage: 1.2,
      summary: "短周期趋势延续，建议顺势持有轻仓多头。"
    },
    "Global Macro PM": {
      signal: "neutral_to_long",
      confidence: 0.71,
      hedgeRatio: 0.35,
      scenario: "美元阶段性走弱，库存端偏紧支撑油价中枢抬升。",
      note: "关注 OPEC+ 会议与美国库存数据的共振影响。"
    },
    "Physical Hedger": {
      signal: "hedge_upside",
      confidence: 0.83,
      action: "buy_call_spread",
      hedgeWindow: "2w",
      comment: "现货采购成本压力抬升，建议锁定部分上行风险。"
    }
  },
  parameterCorrection: {
    positionSize: 0.16,
    hedgeRatio: 0.42,
    stopLossPct: 0.028,
    takeProfitPct: 0.065,
    rebalanceWindow: "2d",
    note: "建议降低方向性仓位并提升对冲比例，以平衡短期波动。"
  },
  agentFeedItems: [
    {
      id: "sim-cta",
      agentName: "CTA Trend Agent",
      role: "CTA",
      direction: "LONG",
      riskAttitude: "MODERATE",
      rationale: "趋势信号继续偏多，但量价斜率显示不适合激进加仓。",
      confidence: 0.78,
      memory: "上一轮模拟在 71.6 附近建立试探性多头。",
      remark: "若跌破 70.4，优先执行止损而非补仓。",
      updatedAt: new Date().toISOString(),
      tags: ["trend", "wti", "cta"],
      rawDecisionJson: {
        signal: "long",
        confidence: 0.78,
        targetPriceRange: [70.8, 74.2],
        recommendedLeverage: 1.2,
        summary: "短周期趋势延续，建议顺势持有轻仓多头。"
      },
      parameterCorrection: {
        positionSize: 0.16,
        stopLossPct: 0.028
      }
    },
    {
      id: "sim-macro",
      agentName: "Macro Allocation Agent",
      role: "Global Macro PM",
      direction: "NEUTRAL TO LONG",
      riskAttitude: "BALANCED",
      rationale: "宏观流动性与供需预期共振偏多，但美元变量仍可能压制上行节奏。",
      confidence: 0.71,
      memory: "近期更偏向用对冲替代单边加仓。",
      remark: "建议提高事件窗口前的风险预算敏感度。",
      updatedAt: new Date().toISOString(),
      tags: ["macro", "allocation", "hedge"],
      rawDecisionJson: {
        signal: "neutral_to_long",
        confidence: 0.71,
        hedgeRatio: 0.35,
        scenario: "美元阶段性走弱，库存端偏紧支撑油价中枢抬升。",
        note: "关注 OPEC+ 会议与美国库存数据的共振影响。"
      },
      parameterCorrection: {
        hedgeRatio: 0.42,
        rebalanceWindow: "2d"
      }
    },
    {
      id: "sim-hedger",
      agentName: "Physical Hedge Agent",
      role: "Physical Hedger",
      direction: "HEDGE UPSIDE",
      riskAttitude: "CONSERVATIVE",
      rationale: "现货端更关注采购成本稳定性，因此优先锁定上行风险暴露。",
      confidence: 0.83,
      memory: "企业库存天数回落，短期采购窗口更依赖衍生品保护。",
      remark: "使用价差期权可降低纯买入期权的时间价值损耗。",
      updatedAt: new Date().toISOString(),
      tags: ["hedging", "options", "physical"],
      rawDecisionJson: {
        signal: "hedge_upside",
        confidence: 0.83,
        action: "buy_call_spread",
        hedgeWindow: "2w",
        comment: "现货采购成本压力抬升，建议锁定部分上行风险。"
      },
      parameterCorrection: {
        hedgeRatio: 0.42,
        takeProfitPct: 0.065
      }
    }
  ]
};
