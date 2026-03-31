import type { PredictionResult, PredictionRunRequest } from "@/types/predict";
import { adaptPredictionResult, type PredictRunRawResponse } from "./adapters/predictAdapter";
import { requestWithFallback } from "./http";

export interface PredictRequest {
  modelType: string;
  horizon?: number | string;
}

function normalizeHorizon(value: number | string | undefined): string {
  if (typeof value === "number" && Number.isFinite(value)) {
    return `${value}d`;
  }

  if (typeof value === "string" && value.trim()) {
    return value.endsWith("d") ? value : `${value}d`;
  }

  return "1d";
}

function toRunRequest(payload: PredictRequest): PredictionRunRequest {
  return {
    target: payload.modelType,
    horizon: normalizeHorizon(payload.horizon),
    payload: {},
    asOf: new Date().toISOString()
  };
}

function buildMockRawResponse(request: PredictionRunRequest): PredictRunRawResponse {
  const baseValueMap: Record<string, number> = {
    "USD/CNY": 7.21,
    "EUR/CNY": 7.83,
    "JPY/CNY": 0.0482,
    WTI: 78.64
  };
  const baseValue = baseValueMap[request.target] ?? 1;
  const trend = request.target === "WTI" ? "Range-bound to slightly stronger" : "Mild fluctuation";
  const risk = request.target === "WTI" ? "Watch inventory and geopolitical updates" : "Watch USD trend and policy expectations";

  return {
    runId: `mock-${request.target}-${Date.now()}`,
    target: request.target,
    horizon: request.horizon,
    forecast: [
      {
        time: "D+1",
        value: Number(baseValue.toFixed(4))
      }
    ],
    summary: {
      trend,
      risk,
      confidence: request.target === "WTI" ? 0.76 : 0.72,
      explanation: `${request.target} next-day single-point output is available. Extended explanation fields are pending backend finalization.`
    },
    explain: `${request.target} next-day single-point output is available in the current frontend branch.`,
    generatedAt: new Date().toISOString()
  };
}

export function runPrediction(payload: PredictRequest) {
  const request = toRunRequest(payload);

  return requestWithFallback<PredictRunRawResponse, PredictionResult>({
    path: "/api/predict",
    init: {
      method: "POST",
      body: JSON.stringify(request)
    },
    mapReal: (data) => adaptPredictionResult(data, request),
    mocker: async () => adaptPredictionResult(buildMockRawResponse(request), request)
  });
}

export function getLatestPrediction(payload: PredictRequest = { modelType: "USD/CNY", horizon: 1 }) {
  const request = toRunRequest(payload);

  return requestWithFallback<PredictRunRawResponse, PredictionResult>({
    path: "/api/predict/latest",
    init: {
      method: "GET"
    },
    mapReal: (data) => adaptPredictionResult(data, request),
    mocker: async () => adaptPredictionResult(buildMockRawResponse(request), request)
  });
}
