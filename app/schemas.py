# app/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class TimePoint(BaseModel):
    t: datetime
    v: float


class Event(BaseModel):
    occurredAt: datetime
    eventType: str
    intensity: float = 0.0
    summary: Optional[str] = None


class CEEMDANConfig(BaseModel):
    enabled: bool = True
    trials: int = 100
    noise_width: float = 0.2
    max_imfs: int = 8


class SeriesPayload(BaseModel):
    price: list[TimePoint]

    # 用 default_factory 生成新对象，避免共享可变默认值
    indicators: dict[str, list[TimePoint]] = Field(default_factory=dict)

    sentiment_index: Optional[list[TimePoint]] = None


class PredictRequest(BaseModel):
    target: str
    horizon: str
    asOf: Optional[datetime] = None
    series: SeriesPayload

    # 同理：每次实例化都有独立 list
    events: list[Event] = Field(default_factory=list)

    # 子模型默认值：用 default_factory 更安全（避免共享实例）
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
    notes: Optional[str] = None
    lgbm_top_features: Optional[list[dict[str, Any]]] = None
    imf_contrib: Optional[list[dict[str, Any]]] = None
    alpha: Optional[float] = None


class PredictResponse(BaseModel):
    forecast: Forecast
    extremeClass: ExtremeClass
    explain: Explain