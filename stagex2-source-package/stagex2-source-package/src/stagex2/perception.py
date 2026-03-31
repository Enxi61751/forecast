from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import List

from openai import OpenAI

from .schemas import Environment, Event, PerceptionContext, SelfState

LIQUIDITY_STRESS_CRASH_THRESHOLD = 0.8
FORCED_CLOSE_MINUTES = 15
WIDE_SPREAD_THRESHOLD = 0.5

POSITIVE_KEYWORDS = {
    "boom": 1.5,
    "cut": 0.7,
    "shortage": 1.2,
    "breakout": 1.0,
    "new high": 0.8,
    "backwardation": 0.6,
    "war": 0.8,
    "explosion": 1.0,
}
NEGATIVE_KEYWORDS = {
    "ban": 1.2,
    "default": 1.3,
    "miss": 0.9,
    "lower than expected": 1.0,
    "supply surge": 1.3,
    "production increase": 1.0,
    "contango": 0.6,
    "new low": 0.8,
}


def derive_risk_tags(
    environment: Environment,
    self_state: SelfState,
    assumed_horizon: str,
) -> List[str]:
    tags: List[str] = []

    if self_state.unrealized_pnl_pct < -abs(self_state.stop_loss_pct):
        tags.append("CRITICAL_LOSS")

    if (
        environment.tail_risk_report.liquidity_stress > LIQUIDITY_STRESS_CRASH_THRESHOLD
        and environment.tail_risk_report.gamma_profile == "Short Gamma"
    ):
        tags.append("MARKET_CRASH")

    if assumed_horizon in {"Intraday", "intraday"} and environment.session_info.time_to_close < FORCED_CLOSE_MINUTES:
        tags.append("FORCED_CLOSE")

    if not tags:
        tags.append("NORMAL")
    return tags


def _trend_direction(trend_score: float) -> str:
    if trend_score > 0.25:
        return "Up"
    if trend_score < -0.25:
        return "Down"
    return "Flat"


def _momentum_strength(trend_score: float) -> str:
    magnitude = abs(trend_score)
    if magnitude >= 1.5:
        return "Strong"
    if magnitude >= 0.5:
        return "Moderate"
    return "Weak"


def _term_structure_signal(environment: Environment) -> str:
    if environment.factor_snapshot.term_structure == "Backwardation":
        return "Nearby supply is tight and front-month pricing is rich."
    return "Curve is in contango, suggesting inventory comfort or oversupply."


def _spread_zscore(environment: Environment) -> float | None:
    current_spread = environment.factor_snapshot.current_calendar_spread
    historical_mean = environment.factor_snapshot.historical_spread_mean
    historical_std = environment.factor_snapshot.historical_spread_std
    if current_spread is None or historical_mean is None or historical_std is None or historical_std <= 0:
        return None
    return (current_spread - historical_mean) / historical_std


def _execution_cost_state(environment: Environment) -> str:
    spread = environment.market_microstructure.bid_ask_spread
    depth = environment.market_microstructure.order_book_depth
    if depth == "Thin" or spread >= WIDE_SPREAD_THRESHOLD:
        return "High friction: thin book and/or wide spread raise slippage risk."
    if depth == "Normal":
        return "Moderate friction: liquidity is usable but not ideal."
    return "Low friction: deep book and tighter spread favor execution."


def _source_reliability(source: str) -> str:
    normalized = source.lower()
    if "rumor" in normalized or "twitter" in normalized:
        return "Low"
    if "central bank" in normalized or "statement" in normalized or "official" in normalized:
        return "High"
    return "Medium"


def _headline_sentiment(event: Event) -> tuple[float, str]:
    if event.sentiment_score is not None:
        return event.sentiment_score, _sentiment_bias_from_score(event.sentiment_score)

    llm_sentiment = _headline_sentiment_via_llm(event)
    if llm_sentiment is not None:
        return llm_sentiment

    return _headline_sentiment_via_keywords(event)


def _headline_sentiment_via_keywords(event: Event) -> tuple[float, str]:
    text = f"{event.headline} {event.body}".lower()
    score = sum(weight for keyword, weight in POSITIVE_KEYWORDS.items() if keyword in text)
    score -= sum(weight for keyword, weight in NEGATIVE_KEYWORDS.items() if keyword in text)

    if event.impact_type == "Supply Shock":
        if "disruption" in text or "shortage" in text:
            score += 1.0
        if "surge" in text or "increase" in text:
            score -= 1.0
    elif event.impact_type == "Demand Shock":
        if "recovery" in text or "rebound" in text:
            score += 0.8
        if "recession" in text or "collapse" in text:
            score -= 0.8

    return score, _sentiment_bias_from_score(score)


def _sentiment_bias_from_score(score: float) -> str:
    if score > 0.5:
        return "Bullish"
    if score < -0.5:
        return "Bearish"
    return "Neutral"


def _headline_sentiment_via_llm(event: Event) -> tuple[float, str] | None:
    provider = os.getenv("STAGEX2_SENTIMENT_PROVIDER", "llm").lower()
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if provider == "keyword" or not api_key:
        return None

    base_url = os.getenv("STAGEX2_SENTIMENT_BASE_URL") or "https://api.deepseek.com/v1"
    model = os.getenv("STAGEX2_SENTIMENT_MODEL") or os.getenv("STAGEX2_MODEL") or "deepseek-chat"
    try:
        return _headline_sentiment_via_llm_cached(
            event.headline,
            event.body,
            event.source,
            event.impact_type,
            api_key,
            base_url,
            model,
        )
    except Exception:
        return None


@lru_cache(maxsize=128)
def _headline_sentiment_via_llm_cached(
    headline: str,
    body: str,
    source: str,
    impact_type: str,
    api_key: str,
    base_url: str,
    model: str,
) -> tuple[float, str]:
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an NLP sentiment scorer for market-moving news. "
                    "Return JSON only with keys score and bias. "
                    "score must be a float from -3.0 to 3.0. "
                    "bias must be one of Bullish, Bearish, Neutral."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "headline": headline,
                        "body": body,
                        "source": source,
                        "impact_type": impact_type,
                    },
                    ensure_ascii=True,
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    payload = json.loads(content)
    score = float(payload["score"])
    score = max(-3.0, min(3.0, score))
    bias = str(payload.get("bias") or _sentiment_bias_from_score(score))
    if bias not in {"Bullish", "Bearish", "Neutral"}:
        bias = _sentiment_bias_from_score(score)
    return score, bias


def _time_pressure(environment: Environment, assumed_horizon: str) -> str:
    if assumed_horizon in {"Intraday", "intraday"} and environment.session_info.time_to_close < FORCED_CLOSE_MINUTES:
        return "Immediate close pressure: intraday position must be closed."
    if environment.session_info.phase == "Close":
        return "Late-session pressure: closing flow can dominate."
    return "No acute time pressure."


def _pnl_state(self_state: SelfState) -> str:
    if self_state.unrealized_pnl_pct <= -abs(self_state.stop_loss_pct):
        return "Large unrealized loss: stop-loss pressure is active."
    if self_state.unrealized_pnl_pct >= abs(self_state.stop_loss_pct):
        return "Large unrealized gain: take-profit temptation is elevated."
    return "PnL is not at an extreme."


def _capital_state(self_state: SelfState, environment: Environment) -> tuple[str, int]:
    current_price = environment.factor_snapshot.current_price or 0.0
    if current_price <= 0 or self_state.cash_level <= 0 or self_state.max_leverage <= 0:
        return "No buying power available for new exposure.", 0

    leverage_headroom_contracts = max(
        0,
        int((self_state.cash_level * self_state.max_leverage) / current_price),
    )
    if leverage_headroom_contracts == 0:
        return "No buying power available for new exposure.", 0
    if leverage_headroom_contracts < 100:
        return "Limited buying power: new exposure must stay small.", leverage_headroom_contracts
    return "Adequate buying power for new exposure.", leverage_headroom_contracts


def _discipline_state(self_state: SelfState) -> str:
    if self_state.consecutive_losses >= 3:
        return "Discipline warning: three or more consecutive losses suggest pausing or de-risking."
    return "Discipline is stable."


def build_perception_context(
    event: Event,
    environment: Environment,
    self_state: SelfState,
    assumed_horizon: str,
    risk_tags: List[str] | None = None,
) -> PerceptionContext:
    resolved_risk_tags = risk_tags or derive_risk_tags(environment, self_state, assumed_horizon)
    sentiment_score, headline_bias = _headline_sentiment(event)
    capital_state, leverage_headroom_contracts = _capital_state(self_state, environment)
    return PerceptionContext(
        risk_tags=resolved_risk_tags,
        trend_direction=_trend_direction(environment.factor_snapshot.trend_score),  # type: ignore[arg-type]
        momentum_strength=_momentum_strength(environment.factor_snapshot.trend_score),  # type: ignore[arg-type]
        spread_zscore=_spread_zscore(environment),
        term_structure_signal=_term_structure_signal(environment),
        execution_cost_state=_execution_cost_state(environment),
        source_reliability=_source_reliability(event.source),
        headline_sentiment_score=sentiment_score,
        headline_bias=headline_bias,  # type: ignore[arg-type]
        time_pressure=_time_pressure(environment, assumed_horizon),
        pnl_state=_pnl_state(self_state),
        capital_state=capital_state,
        discipline_state=_discipline_state(self_state),
        leverage_headroom_contracts=leverage_headroom_contracts,
    )
