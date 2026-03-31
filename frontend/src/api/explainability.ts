import { requestWithFallback } from "./http";
import type {
  ExplainabilityModelOption,
  ExplainabilityResponse,
  ExplainabilityOverview,
  ExplainabilityRecord,
  ExplainabilityTopFeature
} from "@/types/explainability";

interface ApiEnvelope<T> {
  code: number;
  message: string;
  data: T;
}

interface ExplainabilityOverviewRaw {
  model_name?: string;
  model_type?: string;
  train_lag?: number | null;
  update_period?: number | null;
}

interface ExplainabilityTopFeatureRaw {
  name?: string;
  importance?: number | null;
}

interface ExplainabilityRecordRaw {
  train_date?: string;
  sample_count?: number;
  best_cv_score?: number | null;
  best_params?: Record<string, string | number | boolean | null>;
  summary_plot?: string;
  bar_plot?: string;
  top_features?: ExplainabilityTopFeatureRaw[];
  conclusion?: string | null;
}

interface ExplainabilityResponseRaw {
  overview?: ExplainabilityOverviewRaw;
  records?: ExplainabilityRecordRaw[];
}

function unwrapApiResponse<T>(payload: ApiEnvelope<T> | T): T {
  if (
    payload &&
    typeof payload === "object" &&
    "data" in payload &&
    "code" in payload
  ) {
    return (payload as ApiEnvelope<T>).data;
  }
  return payload as T;
}

function toOverview(raw?: ExplainabilityOverviewRaw): ExplainabilityOverview {
  return {
    modelName: raw?.model_name ?? "",
    modelType: raw?.model_type ?? "",
    trainLag: raw?.train_lag ?? null,
    updatePeriod: raw?.update_period ?? null
  };
}

function toTopFeature(raw: ExplainabilityTopFeatureRaw): ExplainabilityTopFeature {
  return {
    name: raw.name ?? "",
    importance: typeof raw.importance === "number" ? raw.importance : 0
  };
}

function toRecord(raw: ExplainabilityRecordRaw): ExplainabilityRecord {
  return {
    trainDate: raw.train_date ?? "",
    sampleCount: raw.sample_count ?? 0,
    bestCvScore: typeof raw.best_cv_score === "number" ? raw.best_cv_score : null,
    bestParams: raw.best_params ?? {},
    summaryPlot: raw.summary_plot ?? "",
    barPlot: raw.bar_plot ?? "",
    topFeatures: Array.isArray(raw.top_features)
      ? raw.top_features.map(toTopFeature)
      : [],
    conclusion: raw.conclusion ?? null
  };
}

function adaptExplainabilityResponse(
  payload: ApiEnvelope<ExplainabilityResponseRaw> | ExplainabilityResponseRaw
): ExplainabilityResponse {
  const data = unwrapApiResponse<ExplainabilityResponseRaw>(payload);

  return {
    overview: toOverview(data?.overview),
    records: Array.isArray(data?.records) ? data.records.map(toRecord) : []
  };
}

function buildMockModelOptions(): ExplainabilityModelOption[] {
  return [
    {
      key: "lgbm",
      label: "Model-LGBM_GS-u100-l700-p1-dataset_wti_return_new"
    },
    {
      key: "de",
      label: "Model-DE_GS-u100-l700-p1-dataset_wti_return_new"
    }
  ];
}

function buildMockExplainability(modelKey: string): ExplainabilityResponse {
  if (modelKey === "de") {
    return {
      overview: {
        modelName: "Model-DE_GS-u100-l700-p1-dataset_wti_return_new",
        modelType: "DoubleEnsemble",
        trainLag: 700,
        updatePeriod: 100
      },
      records: [
        {
          trainDate: "20240101",
          sampleCount: 700,
          bestCvScore: -0.00052,
          bestParams: {
            n_models: 4,
            SR_enabled: true,
            FS_enabled: true,
            learning_rate: 0.03
          },
          summaryPlot: "/explainability-assets/de/20240101/shap_summary_20240101.png",
          barPlot: "/explainability-assets/de/20240101/shap_bar_20240101.png",
          topFeatures: [
            { name: "wti_vol_20d", importance: 0.19 },
            { name: "diesel_wti_spread", importance: 0.16 },
            { name: "rig_count_neg_growth", importance: 0.12 },
            { name: "dxy_change_5d", importance: 0.10 }
          ],
          conclusion: "DoubleEnsemble 更关注波动率、价差与供给侧变化。"
        }
      ]
    };
  }

  return {
    overview: {
      modelName: "Model-LGBM_GS-u100-l700-p1-dataset_wti_return_new",
      modelType: "LightGBM",
      trainLag: 700,
      updatePeriod: 100
    },
    records: [
      {
        trainDate: "20240101",
        sampleCount: 700,
        bestCvScore: -0.0006274783713074634,
        bestParams: {
          feature_fraction: 1.0,
          lambda_l2: 5,
          learning_rate: 0.03,
          max_depth: 3,
          min_data_in_leaf: 20,
          n_estimators: 20
        },
        summaryPlot: "/explainability-assets/lgbm/20240101/shap_summary_20240101.png",
        barPlot: "/explainability-assets/lgbm/20240101/shap_bar_20240101.png",
        topFeatures: [
          { name: "wti_vol_20d", importance: 0.21 },
          { name: "brent_wti_spread", importance: 0.18 },
          { name: "dxy_change_5d", importance: 0.14 },
          { name: "wti_momentum_10d", importance: 0.11 },
          { name: "wti_vol_10d", importance: 0.09 }
        ],
        conclusion: "近期波动率、价差与美元指数变化是影响预测的关键因素。"
      }
    ]
  };
}

export function getExplainabilityModels() {
  return requestWithFallback<
    ApiEnvelope<ExplainabilityModelOption[]> | ExplainabilityModelOption[],
    ExplainabilityModelOption[]
  >({
    path: "/api/explainability/models",
    init: {
      method: "GET"
    },
    mapReal: (data) => unwrapApiResponse<ExplainabilityModelOption[]>(data),
    mocker: async () => buildMockModelOptions()
  });
}

export function getExplainabilityByModel(modelKey: string) {
  return requestWithFallback<
    ApiEnvelope<ExplainabilityResponseRaw> | ExplainabilityResponseRaw,
    ExplainabilityResponse
  >({
    path: `/api/explainability/${modelKey}`,
    init: {
      method: "GET"
    },
    mapReal: (data) => adaptExplainabilityResponse(data),
    mocker: async () => buildMockExplainability(modelKey)
  });
}