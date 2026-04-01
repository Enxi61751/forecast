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

  const timeout = setTimeout(() => {
    controller.abort();
  }, API_TIMEOUT_MS);

  try {
    const method = init?.method?.toUpperCase() || "GET";
    const shouldSetJsonHeader = method !== "GET" && method !== "HEAD";

    const response = await fetch(buildUrl(path), {
      ...init,
      headers: {
        ...(shouldSetJsonHeader ? { "Content-Type": "application/json" } : {}),
        ...(init?.headers || {})
      },
      signal: controller.signal
    });

    // ✅ HTTP错误（500 / 404 等）
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    const data = (await response.json()) as ApiResponseEnvelope<T> | T;

    // ✅ 后端统一封装结构 {code, message, data}
    if (typeof data === "object" && data !== null && "code" in data && "data" in data) {
      const envelope = data as ApiResponseEnvelope<T>;
      if (envelope.code !== 0) {
        throw new Error(envelope.message || "API returned error");
      }
      return envelope.data;
    }

    return data as T;
  } catch (error: unknown) {
    // ✅ 关键：识别 AbortError（超时）
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`请求超时：超过 ${API_TIMEOUT_MS}ms 未返回（可能是模型服务未响应）`);
    }

    // 其他错误直接抛出
    if (error instanceof Error) {
      throw error;
    }

    throw new Error("未知网络错误");
  } finally {
    clearTimeout(timeout);
  }
}

export async function requestWithFallback<TReal, TOut>(
  options: RequestWithFallbackOptions<TReal, TOut>
): Promise<TOut> {
  const useMockDirectly = API_MODE === "mock";

  if (useMockDirectly) {
    return options.mocker();
  }

  try {
    const real = await fetchJson<TReal>(options.path, options.init);
    return options.mapReal ? options.mapReal(real) : (real as unknown as TOut);
  } catch (error) {
    // 自动降级到 mock
    if (API_MODE === "auto") {
      console.warn(`Fallback to mock for ${options.path}`, error);
      return options.mocker();
    }

    throw error;
  }
}