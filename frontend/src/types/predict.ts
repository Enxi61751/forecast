export type PredictTarget = "USD/CNY" | "EUR/CNY" | "JPY/CNY" | "WTI";
export type PredictHorizon = "1d" | "7d" | "30d";

export interface PredictionRunRequest {
  target: string;
  horizon: string;
  payload: Record<string, unknown>;
  asOf?: string;
}

export interface PredictionPoint {
  time: string;
  value: number;
}

export interface PredictionSummary {
  trend: string;
  risk: string;
  confidence: number;
}

export interface PredictionResult {
  runId: string;
  target: string;
  horizon: string;
  forecast: PredictionPoint[];
  lowerBound: PredictionPoint[];
  upperBound: PredictionPoint[];
  summary: PredictionSummary;
  reportPreview: string;
  generatedAt: string;
}

export type RunPhase = "idle" | "running" | "success" | "error";
export type RunStage = "idle" | "running" | "completed" | "failed";

export interface RunStatus {
  runId: string;
  stage: RunStage;
  progress: number;
  message: string;
}

export interface PredictionRunState {
  phase: RunPhase;
  runId: string | null;
  progress: number;
  message: string;
  error: string | null;
}

export interface ReportData {
  id: string;
  runId: string;
  title: string;
  content: string;
  createdAt: string;
}
