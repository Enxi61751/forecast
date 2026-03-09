export type LoadStatus = "idle" | "loading" | "success" | "empty" | "error";

export interface ApiResponseEnvelope<T> {
  code: number;
  message: string;
  data: T;
}

export interface SelectOption {
  label: string;
  value: string;
}
