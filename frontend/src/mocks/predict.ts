import { MOCK_RUN_OUTCOME } from "@/api/config";
import type { PredictionResult, PredictionRunRequest, ReportData, RunStage, RunStatus } from "@/types/predict";

const runStatusCursor = new Map<string, number>();

interface MockStatusStep {
  stage: RunStage;
  progress: number;
  message: string;
}

function buildSeries(base: number): number[] {
  return [
    Number((base * 0.998).toFixed(4)),
    Number((base * 1.001).toFixed(4)),
    Number((base * 1.005).toFixed(4)),
    Number((base * 1.006).toFixed(4)),
    Number((base * 1.003).toFixed(4)),
    Number((base * 1.001).toFixed(4)),
    Number((base * 1.004).toFixed(4))
  ];
}

function buildDates(): string[] {
  return ["D+1", "D+2", "D+3", "D+4", "D+5", "D+6", "D+7"];
}

function basePriceByTarget(target: string): number {
  if (target === "EUR/CNY") return 7.84;
  if (target === "JPY/CNY") return 0.048;
  if (target === "WTI") return 76.2;
  return 7.18;
}

function getMockStatusSteps(): MockStatusStep[] {
  if (MOCK_RUN_OUTCOME === "error") {
    return [
      { stage: "running", progress: 20, message: "正在拉取特征数据" },
      { stage: "running", progress: 58, message: "正在执行模型推理" },
      { stage: "failed", progress: 100, message: "推理服务返回异常，请稍后重试" }
    ];
  }

  return [
    { stage: "running", progress: 18, message: "正在拉取特征数据" },
    { stage: "running", progress: 55, message: "正在执行模型推理" },
    { stage: "completed", progress: 100, message: "预测任务完成" }
  ];
}

export async function runMockPrediction(req: PredictionRunRequest): Promise<PredictionResult> {
  await new Promise((resolve) => setTimeout(resolve, 680));
  const base = basePriceByTarget(req.target);
  const raw = buildSeries(base);
  const dates = buildDates();
  const runId = `mock-run-${Date.now()}`;
  runStatusCursor.set(runId, 0);

  return {
    runId,
    target: req.target,
    horizon: req.horizon,
    forecast: dates.map((time, index) => ({ time, value: raw[index] })),
    lowerBound: dates.map((time, index) => ({ time, value: Number((raw[index] * 0.992).toFixed(4)) })),
    upperBound: dates.map((time, index) => ({ time, value: Number((raw[index] * 1.008).toFixed(4)) })),
    summary: {
      trend: "短期偏震荡上行",
      risk: "需关注突发事件与情绪放大效应",
      confidence: 0.83
    },
    reportPreview: "模型判断未来一周波动中枢略有抬升，建议结合新闻情绪与库存数据动态管理风险敞口。",
    generatedAt: new Date().toISOString()
  };
}

export async function getMockLatestPrediction(target: string, horizon: string): Promise<PredictionResult> {
  return runMockPrediction({
    target,
    horizon,
    payload: {
      source: "latest-cache"
    },
    asOf: new Date().toISOString()
  });
}

export async function generateMockReport(runId: string): Promise<{ reportId: string }> {
  await new Promise((resolve) => setTimeout(resolve, 280));
  return { reportId: `mock-report-${runId}` };
}

export async function getMockReport(reportId: string, runId = "mock-run"): Promise<ReportData> {
  await new Promise((resolve) => setTimeout(resolve, 260));
  return {
    id: reportId,
    runId,
    title: "AI 风险报告",
    content:
      "1. 预测结论: 未来周期主趋势偏稳，局部可能出现尖峰波动。\n2. 风险提示: 重点监控地缘冲突、能源库存变化、政策信号。\n3. 建议: 采用分层止损与仓位动态调节策略。",
    createdAt: new Date().toISOString()
  };
}

export async function getMockRunStatus(runId: string): Promise<RunStatus> {
  await new Promise((resolve) => setTimeout(resolve, 260));
  const steps = getMockStatusSteps();
  const cursor = runStatusCursor.get(runId) ?? 0;
  const safeIndex = Math.min(cursor, steps.length - 1);
  const step = steps[safeIndex];
  runStatusCursor.set(runId, Math.min(cursor + 1, steps.length - 1));

  return {
    runId,
    stage: step.stage,
    progress: step.progress,
    message: step.message
  };
}
