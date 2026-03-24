import type { BacktestApiResult } from "@/types/backtest";

export async function getBacktestSummary(): Promise<BacktestApiResult> {
  return {
    available: false,
    message: "策略回测接口尚未合并到当前分支，前端先展示 unavailable 状态。",
    data: null
  };
}
