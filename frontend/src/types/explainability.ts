export interface ExplainabilityModelOption {
  key: string;
  label: string;
}

export interface ExplainabilityOverview {
  modelName: string;
  modelType: string;
  trainLag: number | null;
  updatePeriod: number | null;
}

export interface ExplainabilityTopFeature {
  name: string;
  importance: number;
}

export interface ExplainabilityRecord {
  trainDate: string;
  sampleCount: number;
  bestCvScore: number | null;
  bestParams: Record<string, string | number | boolean | null>;
  summaryPlot: string;
  barPlot: string;
  topFeatures: ExplainabilityTopFeature[];
  conclusion: string | null;
}

export interface ExplainabilityResponse {
  overview: ExplainabilityOverview;
  records: ExplainabilityRecord[];
}