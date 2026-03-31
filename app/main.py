from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.pipeline import PredictPipeline
from app.schemas import (
    PredictRequest,
    PredictResponse,
    Forecast,
    ExtremeClass,
    Explain,
    TimePoint,
)

<<<<<<< HEAD
app = FastAPI(title="CitiCup Model Service", version="0.1.0")
=======

import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Any

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic import BaseModel, Field
app = FastAPI(title="CitiCup Model Service", version="0.1.0")
def _to_jsonable(obj):
    if obj is None:
        return None

    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if isinstance(obj, (np.floating,)):
        return float(obj)

    if isinstance(obj, (np.integer,)):
        return int(obj)

    if isinstance(obj, (np.bool_,)):
        return bool(obj)

    return obj
>>>>>>> c3c3a7b (save local files)
pipe = PredictPipeline()


# ── Sentiment endpoint schemas ────────────────────────────────────────────────

class SentimentRequest(BaseModel):
    source: str
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    publishedAt: str  # ISO datetime string


class ExtremeEventDto(BaseModel):
    eventType: str
    summary: str
    intensity: float
    occurredAt: str


class SentimentResponseDto(BaseModel):
    sentiment: float
    confidence: float
<<<<<<< HEAD
    extremeEvents: List[ExtremeEventDto] = []
=======
    extremeEvents: List[ExtremeEventDto] = Field(default_factory=list)
>>>>>>> c3c3a7b (save local files)


def _keyword_sentiment(text: str) -> float:
    """Simple keyword-based sentiment scorer for oil market news."""
    text_lower = text.lower()
    bullish = [
        "rise", "rising", "surge", "surging", "rally", "rallying", "gain",
        "increase", "higher", "upturn", "recovery", "demand", "tight supply",
        "opec cut", "supply cut", "geopolitical tension", "conflict",
    ]
    bearish = [
        "fall", "falling", "drop", "dropping", "plunge", "decline", "lower",
        "decrease", "downturn", "recession", "oversupply", "glut", "weak demand",
        "price war", "opec increase", "supply increase", "slowdown",
    ]
    score = sum(1 for w in bullish if w in text_lower) - sum(
        1 for w in bearish if w in text_lower
    )
    # Normalise to [-1, 1]
    return max(-1.0, min(1.0, score * 0.2))


def _llm_sentiment(text: str) -> tuple[float, float]:
    """Call DeepSeek API for sentiment scoring. Returns (sentiment, confidence)."""
    try:
        import httpx

        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not api_key:
            return None, None

        prompt = (
            "You are an oil market analyst. Given the following news article, "
            "output ONLY a JSON object with two fields:\n"
            '  "sentiment": a float in [-1.0, 1.0] where -1=very bearish, '
            "0=neutral, 1=very bullish for oil prices\n"
            '  "confidence": a float in [0.0, 1.0]\n\n'
            f"Article:\n{text[:1500]}"
        )

        resp = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            timeout=15.0,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        import json, re
        m = re.search(r"\{[^}]+\}", content)
        if m:
            data = json.loads(m.group())
            return float(data.get("sentiment", 0.0)), float(data.get("confidence", 0.7))
    except Exception:
        pass
    return None, None


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/sentiment/score", response_model=SentimentResponseDto)
def sentiment_score(req: SentimentRequest):
    text = f"{req.title}\n{req.content or ''}"

    # Try LLM first; fall back to keyword heuristic
    sent, conf = _llm_sentiment(text)
    if sent is None:
        sent = _keyword_sentiment(text)
        conf = 0.6

    # Simple extreme-event detection: high absolute sentiment
    extreme_events: List[ExtremeEventDto] = []
    if abs(sent) >= 0.6:
        extreme_events.append(
            ExtremeEventDto(
                eventType="price_shock",
                summary=req.title[:200],
                intensity=abs(sent),
                occurredAt=req.publishedAt,
            )
        )

    return SentimentResponseDto(sentiment=sent, confidence=conf, extremeEvents=extreme_events)


def _parse_horizon_days(horizon: str) -> int:
    """Parse horizon string like '1d', '7d', '30d' into number of days."""
    h = (horizon or "1d").strip().lower()
    if h.endswith("d"):
        try:
            return max(1, int(h[:-1]))
        except ValueError:
            pass
    return 1


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        y_final, extreme, explain, raw = pipe.run(req)

        base_time = req.asOf or datetime.now(timezone.utc)
        n_days = _parse_horizon_days(req.horizon)

        # Generate multi-step forecast: compound the single-step return
        # y_final is the T+1 price; for T+k we apply the same daily change ratio
        last_price = (float(req.series.price[-1].v)
                      if req.series is not None and req.series.price
                      else y_final)
        daily_return = (y_final / last_price - 1.0) if last_price > 0 else 0.0

        point_series: List[TimePoint] = []
        lower_series: List[TimePoint] = []
        upper_series: List[TimePoint] = []

        model_outputs = explain.get("model_outputs", {}) if isinstance(explain, dict) else {}
        lower_90 = model_outputs.get("lower_90")
        upper_90 = model_outputs.get("upper_90")

        price = y_final
        for k in range(1, n_days + 1):
            t_k = base_time + timedelta(days=k)
            if k == 1:
                p_k = y_final
            else:
                # Simple compounding: apply same daily return for subsequent days
                p_k = last_price * ((1.0 + daily_return) ** k)
            point_series.append(TimePoint(t=t_k, v=float(p_k)))

            # Confidence interval widens with horizon (sqrt-of-time rule)
            spread_factor = k ** 0.5
            lo = lower_90 if (lower_90 is not None and k == 1) else p_k * (1 - 0.03 * spread_factor)
            hi = upper_90 if (upper_90 is not None and k == 1) else p_k * (1 + 0.03 * spread_factor)
            lower_series.append(TimePoint(t=t_k, v=float(lo)))
            upper_series.append(TimePoint(t=t_k, v=float(hi)))

<<<<<<< HEAD
=======
        raw = _to_jsonable(raw)
        explain = _to_jsonable(explain)

>>>>>>> c3c3a7b (save local files)
        forecast = Forecast(
            point=point_series,
            lower=lower_series,
            upper=upper_series,
            raw=raw,
        )

        return PredictResponse(
            forecast=forecast,
            extremeClass=ExtremeClass(
                label=str(extreme["label"]),
                prob=float(extreme["prob"]),
            ),
            explain=Explain(**explain),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"predict failed: {str(e)}")