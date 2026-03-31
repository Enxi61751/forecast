from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, ConfigDict


class TimePoint(BaseModel):
    t: datetime
    v: float


class Event(BaseModel):
    occurredAt: datetime
    eventType: str
    intensity: float = 0.0
    summary: Optional[str] = None


class CEEMDANConfig(BaseModel):
<<<<<<< HEAD
    enabled: bool = False  # default off; only on if client explicitly enables
=======
    enabled: bool = False
>>>>>>> c3c3a7b (save local files)
    trials: int = 100
    noise_width: float = 0.2
    max_imfs: int = 8
    seed: Optional[int] = 42


class SeriesPayload(BaseModel):
    price: list[TimePoint] = Field(default_factory=list)
    indicators: dict[str, list[TimePoint]] = Field(default_factory=dict)
    sentiment_index: Optional[list[TimePoint]] = None


class PredictRequest(BaseModel):
    target: str
    horizon: str
    asOf: Optional[datetime] = None
<<<<<<< HEAD
    # series is optional: if not provided, pipeline falls back to pre-computed model predictions
=======
>>>>>>> c3c3a7b (save local files)
    series: Optional[SeriesPayload] = None
    events: list[Event] = Field(default_factory=list)
    ceemdan: CEEMDANConfig = Field(default_factory=CEEMDANConfig)


class Forecast(BaseModel):
    point: list[TimePoint]
    lower: Optional[list[TimePoint]] = None
    upper: Optional[list[TimePoint]] = None
    raw: Optional[dict[str, Any]] = None


class ExtremeClass(BaseModel):
    label: str
    prob: float


<<<<<<< HEAD
class Explain(BaseModel):
    # Suppress Pydantic v2 warning about "model_" protected namespace
=======
class FeatureImportanceItem(BaseModel):
    feature: str
    group: str
    avg_weight: float


class ChartSeriesItem(BaseModel):
    name: str
    value: float
    group: Optional[str] = None


class TFTExplain(BaseModel):
    quantiles: Optional[list[float]] = None
    median_prediction: Optional[float] = None
    feature_importance: Optional[list[FeatureImportanceItem]] = None
    hist_feature_importance: Optional[list[FeatureImportanceItem]] = None
    known_future_feature_importance: Optional[list[FeatureImportanceItem]] = None
    charts: Optional[dict[str, list[ChartSeriesItem]]] = None
    raw: Optional[dict[str, Any]] = None


class Explain(BaseModel):
>>>>>>> c3c3a7b (save local files)
    model_config = ConfigDict(protected_namespaces=())

    notes: Optional[str] = None
    lgbm_top_features: Optional[list[dict[str, Any]]] = None
    imf_contrib: Optional[list[dict[str, Any]]] = None
    alpha: Optional[float] = None
    ceemdan: Optional[dict[str, Any]] = None
    model_outputs: Optional[dict[str, Any]] = None
<<<<<<< HEAD
=======
    tft: Optional[TFTExplain] = None
>>>>>>> c3c3a7b (save local files)


class PredictResponse(BaseModel):
    forecast: Forecast
    extremeClass: ExtremeClass
<<<<<<< HEAD
    explain: Explain
=======
    explain: Explain
>>>>>>> c3c3a7b (save local files)
