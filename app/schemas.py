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
    enabled: bool = False  # default off; only on if client explicitly enables
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
    # series is optional: if not provided, pipeline falls back to pre-computed model predictions
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


class Explain(BaseModel):
    # Suppress Pydantic v2 warning about "model_" protected namespace
    model_config = ConfigDict(protected_namespaces=())

    notes: Optional[str] = None
    lgbm_top_features: Optional[list[dict[str, Any]]] = None
    imf_contrib: Optional[list[dict[str, Any]]] = None
    alpha: Optional[float] = None
    ceemdan: Optional[dict[str, Any]] = None
    model_outputs: Optional[dict[str, Any]] = None


class PredictResponse(BaseModel):
    forecast: Forecast
    extremeClass: ExtremeClass
    explain: Explain
