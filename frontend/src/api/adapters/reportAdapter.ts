import type { ReportData } from "@/types/predict";

// TODO: align generate/detail response fields with finalized report endpoints.
export type ReportGenerateRawResponse = number | string | { reportId?: unknown; id?: unknown };

export interface ReportDetailRawResponse {
  id?: unknown;
  runId?: unknown;
  predictionRunId?: unknown;
  title?: unknown;
  reportText?: unknown;
  content?: unknown;
  createdAt?: unknown;
}

function toText(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

export function adaptGeneratedReportId(raw: ReportGenerateRawResponse, runId: string): string {
  if (typeof raw === "number" || typeof raw === "string") {
    return String(raw);
  }

  if (typeof raw === "object" && raw !== null) {
    const value = raw.reportId ?? raw.id;
    if (typeof value === "number" || typeof value === "string") {
      return String(value);
    }
  }

  return `mock-report-${runId}`;
}

export function adaptReportData(raw: ReportDetailRawResponse, reportId: string): ReportData {
  return {
    id: toText(raw.id, reportId),
    runId: toText(raw.predictionRunId, toText(raw.runId, "unknown-run")),
    title: toText(raw.title, "AI Risk Report"),
    content: toText(raw.reportText, toText(raw.content, "Report content is unavailable.")),
    createdAt: toText(raw.createdAt, new Date().toISOString())
  };
}
