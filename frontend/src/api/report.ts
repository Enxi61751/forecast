import { requestWithFallback } from "./http";

export interface ReportItem {
  id: number;
  title: string;
  createdAt?: string;
  type?: string;
}

export interface ReportListResult {
  list: ReportItem[];
  total: number;
}

export interface GenerateReportRequest {
  predictionRunId?: number;
  modelType?: string;
  horizon?: number;
}

export interface GenerateReportResult {
  id: number;
  title: string;
  createdAt: string;
  type: string;
  content: string;
}

export function getReportList() {
  return requestWithFallback<ReportListResult, ReportListResult>({
    path: "/api/report/list",
    init: {
      method: "GET"
    },
    mocker: async () => ({
      total: 1,
      list: [
        {
          id: 1,
          title: "Mock Report",
          createdAt: new Date().toISOString(),
          type: "summary"
        }
      ]
    })
  });
}

export function generateReport(payload: GenerateReportRequest) {
  return requestWithFallback<GenerateReportResult, GenerateReportResult>({
    path: "/api/report/generate",
    init: {
      method: "POST",
      body: JSON.stringify(payload)
    },
    mocker: async () => ({
      id: 1,
      title: "油价预测分析报告",
      createdAt: new Date().toISOString(),
      type: "summary",
      content:
        "根据当前模型输出与历史走势分析，未来一段时间油价可能呈现小幅波动趋势，建议结合国际原油价格、供需关系与市场情绪综合判断。"
    })
  });
}