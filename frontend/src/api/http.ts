import type { ApiResponseEnvelope } from "@/types/common";
import { API_BASE_URL, API_MODE, API_TIMEOUT_MS } from "./config";

interface RequestWithFallbackOptions<TReal, TOut> {
  path: string;
  init?: RequestInit;
  mocker: () => Promise<TOut> | TOut;
  mapReal?: (data: TReal) => TOut;
}

function buildUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${API_BASE_URL}${path}`;
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    const response = await fetch(buildUrl(path), {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {})
      },
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = (await response.json()) as ApiResponseEnvelope<T> | T;

    if (typeof data === "object" && data !== null && "code" in data && "data" in data) {
      const envelope = data as ApiResponseEnvelope<T>;
      if (envelope.code !== 0) {
        throw new Error(envelope.message || "API returned error");
      }
      return envelope.data;
    }

    return data as T;
  } finally {
    clearTimeout(timeout);
  }
}

export async function requestWithFallback<TReal, TOut>(options: RequestWithFallbackOptions<TReal, TOut>): Promise<TOut> {
  const useMockDirectly = API_MODE === "mock";
  if (useMockDirectly) {
    return options.mocker();
  }

  try {
    const real = await fetchJson<TReal>(options.path, options.init);
    return options.mapReal ? options.mapReal(real) : (real as unknown as TOut);
  } catch (error) {
    if (API_MODE === "auto") {
      console.warn(`Fallback to mock for ${options.path}`, error);
      return options.mocker();
    }
    throw error;
  }
}
