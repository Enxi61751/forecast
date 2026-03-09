import type { RunStatus, RunStage } from "@/types/predict";

// TODO: align stage/status/state field naming with finalized status endpoint.
export interface RunStatusRawResponse {
  runId?: unknown;
  stage?: unknown;
  status?: unknown;
  state?: unknown;
  progress?: unknown;
  message?: unknown;
}

function toText(value: unknown, fallback: string): string {
  if (typeof value === "string" && value.trim()) {
    return value;
  }
  return fallback;
}

function toFiniteNumber(value: unknown, fallback = 0): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function normalizeStage(stageInput: unknown): RunStage {
  const stage = String(stageInput ?? "").toLowerCase();

  if (stage === "completed" || stage === "success" || stage === "done") {
    return "completed";
  }

  if (stage === "failed" || stage === "error") {
    return "failed";
  }

  if (stage === "idle" || stage === "pending" || stage === "queued") {
    return "idle";
  }

  return "running";
}

export function adaptRunStatus(raw: RunStatusRawResponse, fallbackRunId: string): RunStatus {
  const stage = normalizeStage(raw.stage ?? raw.status ?? raw.state);

  return {
    runId: toText(raw.runId, fallbackRunId),
    stage,
    progress: toFiniteNumber(raw.progress, stage === "completed" || stage === "failed" ? 100 : 0),
    message: toText(
      raw.message,
      stage === "completed"
        ? "Prediction completed"
        : stage === "failed"
          ? "Prediction failed"
          : stage === "idle"
            ? "Task has not started"
            : "Prediction is running"
    )
  };
}
