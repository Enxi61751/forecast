import { generateMockReport, getMockReport } from "@/mocks";
import type { ReportData } from "@/types/predict";
import { adaptGeneratedReportId, adaptReportData, type ReportDetailRawResponse, type ReportGenerateRawResponse } from "./adapters/reportAdapter";
import { requestWithFallback } from "./http";

export async function generateReport(runId: string): Promise<string> {
  return requestWithFallback<ReportGenerateRawResponse, string>({
    path: `/api/report/generate/${encodeURIComponent(runId)}`,
    init: {
      method: "POST"
    },
    mocker: async () => {
      const mock = await generateMockReport(runId);
      return mock.reportId;
    },
    mapReal: (raw) => adaptGeneratedReportId(raw, runId)
  });
}

export async function getReport(reportId: string): Promise<ReportData> {
  return requestWithFallback<ReportDetailRawResponse, ReportData>({
    path: `/api/report/${encodeURIComponent(reportId)}`,
    mocker: () => getMockReport(reportId),
    mapReal: (raw) => adaptReportData(raw, reportId)
  });
}
