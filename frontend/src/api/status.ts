import { requestWithFallback } from "./http";

export interface RunStatus {
  status: string;
  time: string;
}

export function getRunStatus() {
  return requestWithFallback<RunStatus, RunStatus>({
    path: "/api/health",
    mocker: async () => ({
      status: "MOCK-UP",
      time: new Date().toISOString()
    })
  });
}