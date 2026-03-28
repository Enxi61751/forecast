import type { AgentFeedRawResponse } from "@/api/adapters/agentAdapter";

export const mockAgentFeed: AgentFeedRawResponse = {
  asOf: new Date().toISOString(),
  reportTitle: "Agent Daily Report",
  reportBody: `Market Analysis by AI Agents - ${new Date().toLocaleDateString()}

Section 1: Market Overview
The forex market shows mixed signals. USD strength continues against emerging market currencies.

Section 2: Risk Assessment
- USD/CNY: Range-bound with upside bias (confidence: 0.75)
- EUR/CNY: Moderate volatility expected (confidence: 0.68)
- WTI: Supply concerns support prices (confidence: 0.72)

Section 3: Trading Recommendations
Monitor US economic data releases. Risk management crucial given current volatility backdrop.`,
  sections: [
    {
      id: "section-1",
      title: "Forex Market Analysis",
      items: [
        {
          id: "agent-1",
          agentName: "FX Specialist Agent",
          role: "Currency Analyst",
          direction: "NEUTRAL",
          riskAttitude: "MODERATE",
          rationale: "USD strength supported by rate differential expectations, but geopolitical risks limit upside.",
          confidence: 0.73,
          memory: "Tracking USD momentum vs EM currencies",
          remark: "Watch Fed speakers this week",
          updatedAt: new Date().toISOString(),
          tags: ["forex", "technical", "macro"]
        },
        {
          id: "agent-2",
          agentName: "Commodity Trade Agent",
          role: "Commodity Trader",
          direction: "LONG",
          riskAttitude: "CONSERVATIVE",
          rationale: "Oil supply disruptions and demand concerns create range-bound trading opportunity.",
          confidence: 0.68,
          memory: "Monitoring inventory levels and geopolitical events",
          remark: "Key resistance at 80 USD/barrel",
          updatedAt: new Date().toISOString(),
          tags: ["commodities", "energy", "technical"]
        }
      ]
    },
    {
      id: "section-2",
      title: "Risk Management Summary",
      items: [
        {
          id: "agent-3",
          agentName: "Risk Monitor Agent",
          role: "Risk Manager",
          direction: null,
          riskAttitude: "CAUTIOUS",
          rationale: "Elevated volatility in emerging market assets. Position sizing should reflect heightened uncertainty.",
          confidence: 0.81,
          memory: "Tracking VIX and EM volatility indices",
          remark: "Consider tighter stops on intraday trades",
          updatedAt: new Date().toISOString(),
          tags: ["risk", "volatility", "position-management"]
        }
      ]
    }
  ]
};

export async function getMockAgentFeed(): Promise<AgentFeedRawResponse> {
  // Simulate API latency
  await new Promise((resolve) => setTimeout(resolve, 600));
  return mockAgentFeed;
}
