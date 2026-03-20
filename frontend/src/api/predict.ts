import { requestWithFallback } from "./http";

export interface PredictRequest {
  modelType: string;
  horizon?: number;
}

export interface PredictPoint {
  date: string;
  value: number;
}

export interface PredictResult {
  modelType: string;
  result: PredictPoint[];
}

export function runPrediction(payload: PredictRequest) {
  return requestWithFallback<PredictResult, PredictResult>({
    path: "/api/predict",
    init: {
      method: "POST",
      body: JSON.stringify(payload)
    },
    mocker: async () => ({
      modelType: payload.modelType,
      result: [
        { date: "2026-04-01", value: 7.68 },
        { date: "2026-05-01", value: 7.72 }
      ]
    })
  });
}

export function getLatestPrediction() {
  return requestWithFallback<PredictResult, PredictResult>({
    path: "/api/predict/latest",
    init: {
      method: "GET"
    },
    mocker: async () => ({
      modelType: "latest",
      result: [
        { date: "2026-04-01", value: 7.68 },
        { date: "2026-05-01", value: 7.72 }
      ]
    })
  });
}