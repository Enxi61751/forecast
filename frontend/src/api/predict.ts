import { getMockLatestPrediction, runMockPrediction } from "@/mocks";
import type { PredictionResult, PredictionRunRequest } from "@/types/predict";
import { adaptPredictionResult, type PredictLatestRawResponse, type PredictRunRawResponse } from "./adapters/predictAdapter";
import { requestWithFallback } from "./http";

export async function runPrediction(req: PredictionRunRequest): Promise<PredictionResult> {
  return requestWithFallback<PredictRunRawResponse, PredictionResult>({
    path: "/api/predict/run",
    init: {
      method: "POST",
      body: JSON.stringify(req)
    },
    mocker: () => runMockPrediction(req),
    mapReal: (raw) => adaptPredictionResult(raw, req)
  });
}

export async function getLatestPrediction(target: string, horizon: string): Promise<PredictionResult> {
  const encodedTarget = encodeURIComponent(target);
  const encodedHorizon = encodeURIComponent(horizon);

  return requestWithFallback<PredictLatestRawResponse, PredictionResult>({
    path: `/api/predict/latest?target=${encodedTarget}&horizon=${encodedHorizon}`,
    mocker: () => getMockLatestPrediction(target, horizon),
    mapReal: (raw) =>
      adaptPredictionResult(raw, {
        target,
        horizon,
        payload: {}
      })
  });
}
