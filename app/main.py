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

app = FastAPI(title="CitiCup Model Service", version="0.1.0")
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
    extremeEvents: List[ExtremeEventDto] = []


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


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        y_final, extreme, explain, raw = pipe.run(req)

        # 当前先按 T+1 输出；后续可根据 req.horizon 扩展为多步预测
        base_time = req.asOf or datetime.now(timezone.utc)
        t_next = base_time + timedelta(days=1)

        forecast = Forecast(
            point=[TimePoint(t=t_next, v=float(y_final))],
            lower=None,
            upper=None,
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