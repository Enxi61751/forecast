import { getMockRunStatus } from "@/mocks";
import type { RunStatus } from "@/types/predict";
import { adaptRunStatus, type RunStatusRawResponse } from "./adapters/statusAdapter";
import { requestWithFallback } from "./http";

export async function getRunStatus(runId: string): Promise<RunStatus> {
  return requestWithFallback<RunStatusRawResponse, RunStatus>({
    path: `/api/predict/status/${encodeURIComponent(runId)}`,
    mocker: () => getMockRunStatus(runId),
    mapReal: (raw) => adaptRunStatus(raw, runId)
  });
}
