export type ApiMode = "mock" | "real" | "auto";
export type MockRunOutcome = "success" | "error";

const rawMode = (import.meta.env.VITE_API_MODE as string | undefined)?.toLowerCase();
const rawMockRunOutcome = (import.meta.env.VITE_MOCK_RUN_OUTCOME as string | undefined)?.toLowerCase();

export const API_MODE: ApiMode = rawMode === "mock" || rawMode === "real" || rawMode === "auto" ? rawMode : "auto";
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) || "http://localhost:8080";
export const API_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 60000);
export const MOCK_RUN_OUTCOME: MockRunOutcome = rawMockRunOutcome === "error" ? "error" : "success";
