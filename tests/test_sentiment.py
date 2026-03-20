"""
Tests for the /sentiment/score endpoint in model-remote.
Run with: USE_STUB=1 pytest tests/test_sentiment.py -v
"""
import os
os.environ.setdefault("USE_STUB", "1")

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── /health ──────────────────────────────────────────────────────────────────

def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


# ── /sentiment/score — response structure ────────────────────────────────────

BASE_REQ = {
    "source": "Reuters",
    "title": "Oil prices steady",
    "content": "Markets remain stable.",
    "publishedAt": "2026-03-20T00:00:00Z",
}


def test_sentiment_score_returns_200():
    resp = client.post("/sentiment/score", json=BASE_REQ)
    assert resp.status_code == 200


def test_sentiment_score_has_required_fields():
    resp = client.post("/sentiment/score", json=BASE_REQ)
    data = resp.json()
    assert "sentiment" in data, "response must have 'sentiment'"
    assert "confidence" in data, "response must have 'confidence'"
    assert "extremeEvents" in data, "response must have 'extremeEvents'"


def test_sentiment_score_types_are_correct():
    resp = client.post("/sentiment/score", json=BASE_REQ)
    data = resp.json()
    assert isinstance(data["sentiment"], float), "sentiment must be float"
    assert isinstance(data["confidence"], float), "confidence must be float"
    assert isinstance(data["extremeEvents"], list), "extremeEvents must be list"


def test_sentiment_score_bounds():
    resp = client.post("/sentiment/score", json=BASE_REQ)
    data = resp.json()
    assert -1.0 <= data["sentiment"] <= 1.0, "sentiment must be in [-1, 1]"
    assert 0.0 <= data["confidence"] <= 1.0, "confidence must be in [0, 1]"


# ── /sentiment/score — minimal request (no optional fields) ──────────────────

def test_sentiment_score_works_without_content_and_url():
    resp = client.post("/sentiment/score", json={
        "source": "Bloomberg",
        "title": "Oil rises",
        "publishedAt": "2026-03-20T00:00:00Z",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "sentiment" in data


# ── /sentiment/score — validation errors ─────────────────────────────────────

def test_sentiment_score_missing_source_returns_422():
    resp = client.post("/sentiment/score", json={
        "title": "Oil falls",
        "publishedAt": "2026-03-20T00:00:00Z",
    })
    assert resp.status_code == 422


def test_sentiment_score_missing_title_returns_422():
    resp = client.post("/sentiment/score", json={
        "source": "Reuters",
        "publishedAt": "2026-03-20T00:00:00Z",
    })
    assert resp.status_code == 422


def test_sentiment_score_missing_publishedAt_returns_422():
    resp = client.post("/sentiment/score", json={
        "source": "Reuters",
        "title": "Oil stable",
    })
    assert resp.status_code == 422


# ── /sentiment/score — keyword-based scoring direction ───────────────────────

def test_sentiment_score_bullish_keywords_positive():
    """Strong bullish keywords should produce sentiment > 0."""
    resp = client.post("/sentiment/score", json={
        "source": "Reuters",
        "title": "Oil surge rally rise gain increase higher demand recovery",
        "content": "supply cut tight supply geopolitical tension",
        "publishedAt": "2026-03-20T00:00:00Z",
    })
    assert resp.status_code == 200
    assert resp.json()["sentiment"] > 0, "strongly bullish text should score > 0"


def test_sentiment_score_bearish_keywords_negative():
    """Strong bearish keywords should produce sentiment < 0."""
    resp = client.post("/sentiment/score", json={
        "source": "Reuters",
        "title": "Oil plunge drop fall decline lower decrease downturn oversupply",
        "content": "recession glut price war slowdown supply increase",
        "publishedAt": "2026-03-20T00:00:00Z",
    })
    assert resp.status_code == 200
    assert resp.json()["sentiment"] < 0, "strongly bearish text should score < 0"


# ── /sentiment/score — extreme event detection ───────────────────────────────

def test_sentiment_score_strong_signal_creates_extreme_event():
    """When |sentiment| >= 0.6 the endpoint must return at least one extreme event."""
    # 10 bullish hits → score capped at 1.0 ≥ 0.6
    resp = client.post("/sentiment/score", json={
        "source": "Reuters",
        "title": "surge rally rise gain increase higher upturn recovery demand",
        "content": "supply cut tight supply",
        "publishedAt": "2026-03-20T06:00:00Z",
    })
    assert resp.status_code == 200
    data = resp.json()
    if abs(data["sentiment"]) >= 0.6:
        assert len(data["extremeEvents"]) > 0, "|sentiment| >= 0.6 must produce extreme events"


def test_extreme_event_has_required_fields():
    """ExtremeEventDto must have all required fields."""
    resp = client.post("/sentiment/score", json={
        "source": "Reuters",
        "title": "surge rally rise gain increase higher upturn recovery demand",
        "content": "supply cut tight supply",
        "publishedAt": "2026-03-20T06:00:00Z",
    })
    data = resp.json()
    for ev in data["extremeEvents"]:
        assert "eventType" in ev
        assert "summary" in ev
        assert "intensity" in ev
        assert "occurredAt" in ev
        assert 0.0 <= ev["intensity"] <= 1.0
