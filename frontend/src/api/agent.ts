import type { AgentApiResult } from "@/types/agent";

export async function getAgentFeed(): Promise<AgentApiResult> {
  return {
    available: false,
    message: "智能体日报接口尚未合并到当前分支，前端先展示 unavailable 状态。",
    data: null
  };
}
