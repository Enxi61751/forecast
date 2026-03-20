from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Protocol

from agents import Agent, ModelSettings, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel

from .perception import WIDE_SPREAD_THRESHOLD, build_perception_context
from .schemas import AgentActionOutput, Environment, Horizon, InstrumentPref, Event, SelfState


class RoleTemplate(BaseModel):
    persona: str
    attention: List[str]
    utility_function: str
    decision_logic: List[str]
    instrument_pref: InstrumentPref
    horizon: Horizon
    aggressiveness_hint: str
    size_hint: str


ROLE_TEMPLATES: Dict[str, RoleTemplate] = {
    "CTA": RoleTemplate(
        persona="Trend follower who reacts to momentum and technical continuation.",
        attention=[
            "Factor Snapshot trend direction and momentum strength.",
            "Scenario keywords such as breakout, new high, new low, and continuation.",
        ],
        utility_function="Maximize participation in confirmed momentum while avoiding noisy range trading.",
        decision_logic=[
            "If trend is up and the scenario is bullish, add aggressively.",
            "If trend is up but the scenario is a bearish shock, flatten or reverse.",
            "If the market is range-bound, stay flat or trade small.",
        ],
        instrument_pref="front",
        horizon="1w",
        aggressiveness_hint="Usually 0.6 to 0.8, more aggressive on breakouts.",
        size_hint="Size should scale with momentum strength.",
    ),
    "Global Macro PM": RoleTemplate(
        persona="Fundamental macro investor looking for structural mispricing.",
        attention=[
            "Scenario details about war, sanctions, central banks, weather, and macro data.",
            "Tail Risk Report for fragile market states.",
        ],
        utility_function="Maximize long-horizon payoff from structural supply-demand mispricing.",
        decision_logic=[
            "Irreversible supply damage is a strong long.",
            "Global demand deterioration is a short.",
            "If price is rich and the scenario is weak, fade the move.",
        ],
        instrument_pref="back",
        horizon="1m",
        aggressiveness_hint="Usually 0.3 to 0.5 and prefers patient entry.",
        size_hint="Scale size with shock magnitude and structural conviction.",
    ),
    "Physical Hedger": RoleTemplate(
        persona="Commercial hedger who prioritizes supply security and cost certainty over alpha.",
        attention=[
            "Scenario evidence of logistics disruption, low inventory, and force majeure.",
            "Factor Snapshot for nearby supply tightness.",
        ],
        utility_function="Minimize supply disruption risk and lock cost even when price is uncomfortable.",
        decision_logic=[
            "Supply disruption or inventory shortage triggers panic buying.",
            "Rapid price rises can justify defensive hedging.",
            "If risk is triggered, ignore price comfort and get the hedge done.",
        ],
        instrument_pref="front",
        horizon="1d",
        aggressiveness_hint="Usually 0.9 to 1.0 because execution certainty dominates.",
        size_hint="Extreme supply stress should push size toward +3.",
    ),
    "Options Dealer": RoleTemplate(
        persona="Options market maker who manages gamma and volatility exposure under stress.",
        attention=[
            "Tail Risk Report gamma regime and liquidity stress.",
            "Scenario details that can reprice volatility or force dealer hedging.",
        ],
        utility_function="Minimize dealer gamma and volatility risk while keeping options markets tradable.",
        decision_logic=[
            "Short Gamma with rising stress requires urgent defensive hedging.",
            "Volatility shocks should prefer options instruments to express non-linear risk.",
            "When gamma risk is elevated, execution certainty matters more than entry finesse.",
        ],
        instrument_pref="options",
        horizon="1d",
        aggressiveness_hint="Usually 0.8 to 1.0 under stress because hedging urgency dominates.",
        size_hint="Size should scale with gamma stress and volatility shock severity.",
    ),
    "Spread Trader": RoleTemplate(
        persona="Relative-value trader focused on term-structure and mean reversion.",
        attention=[
            "Factor Snapshot term structure slope.",
            "Whether the event is short-term or long-term for the curve.",
        ],
        utility_function="Maximize spread mean-reversion payoff while limiting outright directional exposure.",
        decision_logic=[
            "Short-term supply stress favors long-nearby versus short-far spread positioning.",
            "Large deviations from normal curve shape call for mean reversion.",
            "Keep trades measured and structure-aware.",
        ],
        instrument_pref="spread",
        horizon="3d",
        aggressiveness_hint="Usually around 0.4 and prefers limit execution.",
        size_hint="Normally uses modest directional size such as +/-1.",
    ),
    "News HFT": RoleTemplate(
        persona="Keyword-driven news trader with the fastest reaction and the shortest holding period.",
        attention=[
            "Scenario emotion words such as panic, boom, war, ban, default.",
            "NLP sentiment score and immediate headline polarity.",
        ],
        utility_function="Maximize first-response speed to headline sentiment and flatten quickly afterward.",
        decision_logic=[
            "Positive shock keywords trigger immediate buying.",
            "Negative surprise keywords trigger immediate selling.",
            "The trade is intraday and must be closed quickly.",
        ],
        instrument_pref="front",
        horizon="intraday",
        aggressiveness_hint="Aggressiveness should be 1.0 because speed dominates.",
        size_hint="Single-trade size is small, but still directional and urgent.",
    ),
}


class LLMAdapter(Protocol):
    def complete(self, messages: List[dict[str, str]], schema: dict[str, Any]) -> str:
        ...


class OpenAIAgentsSDKAdapter:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        temperature: float = 0.0,
    ):
        resolved_api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not resolved_api_key:
            raise ValueError("Missing DEEPSEEK_API_KEY or OPENAI_API_KEY for OpenAI Agents SDK adapter.")

        resolved_base_url = base_url or os.getenv("STAGEX2_BASE_URL") or "https://api.deepseek.com"
        resolved_model_name = model_name or os.getenv("STAGEX2_MODEL") or "deepseek-chat"

        set_tracing_disabled(True)
        self.client = AsyncOpenAI(api_key=resolved_api_key, base_url=resolved_base_url)
        self.model = OpenAIChatCompletionsModel(model=resolved_model_name, openai_client=self.client)
        self.model_settings = ModelSettings(temperature=temperature)

    def complete(self, messages: List[dict[str, str]], schema: dict[str, Any]) -> str:
        system_prompt, user_input = _messages_to_agent_input(messages, schema)
        agent = Agent(
            name="stage_x2_agent",
            instructions=system_prompt,
            model=self.model,
            model_settings=self.model_settings,
        )
        result = Runner.run_sync(agent, user_input)
        return _normalize_agent_output(result.final_output)


class DecisionEngine(Protocol):
    def default_horizon_for_role(self, role: str) -> str:
        ...

    def decide(
        self,
        event: Event,
        environment: Environment,
        self_state: SelfState,
        risk_tags: List[str],
    ) -> AgentActionOutput:
        ...


class LLMDecisionEngine:
    def __init__(self, adapter: LLMAdapter):
        self.adapter = adapter

    def default_horizon_for_role(self, role: str) -> str:
        return _role_template(role).horizon

    def decide(
        self,
        event: Event,
        environment: Environment,
        self_state: SelfState,
        risk_tags: List[str],
    ) -> AgentActionOutput:
        perception = build_perception_context(
            event=event,
            environment=environment,
            self_state=self_state,
            assumed_horizon=self.default_horizon_for_role(self_state.role),
            risk_tags=risk_tags,
        )
        messages = build_prompt_messages(
            event=event,
            environment=environment,
            self_state=self_state,
            risk_tags=risk_tags,
            perception=perception,
        )
        raw_output = _extract_json_text(self.adapter.complete(messages, AgentActionOutput.model_json_schema()))
        try:
            payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM output must be valid JSON.") from exc
        action = AgentActionOutput.model_validate(payload)
        return _apply_document_overrides(
            role=self_state.role,
            event=event,
            self_state=self_state,
            environment=environment,
            perception=perception,
            risk_tags=risk_tags,
            action=action,
        )


def _role_template(role: str) -> RoleTemplate:
    template = ROLE_TEMPLATES.get(role)
    if template is None:
        raise ValueError(f"Unsupported role: {role}")
    return template


def _state_context_instructions(risk_tags: List[str]) -> str:
    instructions: List[str] = []
    if "CRITICAL_LOSS" in risk_tags:
        instructions.append(
            "[WARNING] You are in serious loss. Ignore favorable news. "
            "Your primary goal is stop loss. Aggressiveness must be above 0.8."
        )
    if "MARKET_CRASH" in risk_tags:
        instructions.append(
            "[ALERT] Liquidity stress is high and gamma is Short Gamma. "
            "Treat the market as fragile and nonlinear."
        )
    if "FORCED_CLOSE" in risk_tags:
        instructions.append(
            "[TIME LIMIT] If your horizon is Intraday or intraday and time_to_close is near zero, "
            "you must close the position."
        )
    if not instructions:
        instructions.append(
            "Analyze the news impact on supply and demand, then combine it with the current market state."
        )
    return " ".join(instructions)


def build_prompt_messages(
    *,
    event: Event,
    environment: Environment,
    self_state: SelfState,
    risk_tags: List[str],
    perception=None,
) -> List[dict[str, str]]:
    template = _role_template(self_state.role)
    if perception is None:
        perception = build_perception_context(
            event=event,
            environment=environment,
            self_state=self_state,
            assumed_horizon=template.horizon,
            risk_tags=risk_tags,
        )
    system_prompt = (
        f"You are {self_state.role}. "
        f"Persona: {template.persona} "
        f"Attention: {' '.join(template.attention)} "
        f"Utility Function: {template.utility_function} "
        f"Decision logic: {' '.join(template.decision_logic)} "
        f"Output mapping bias: instrument_pref should usually be {template.instrument_pref}; "
        f"horizon should usually be {template.horizon}; {template.aggressiveness_hint} {template.size_hint} "
        f"State context: {_state_context_instructions(risk_tags)} "
        f"Perception summary: trend_direction={perception.trend_direction}; "
        f"momentum_strength={perception.momentum_strength}; "
        f"spread_zscore={perception.spread_zscore}; "
        f"headline_bias={perception.headline_bias}; "
        f"headline_sentiment_score={perception.headline_sentiment_score:.2f}; "
        f"source_reliability={perception.source_reliability}; "
        f"term_structure_signal={perception.term_structure_signal}; "
        f"execution_cost_state={perception.execution_cost_state}; "
        f"time_pressure={perception.time_pressure}; "
        f"pnl_state={perception.pnl_state}; "
        f"capital_state={perception.capital_state}; "
        f"discipline_state={perception.discipline_state}; "
        f"hedger_type={self_state.hedger_type}; "
        f"leverage_headroom_contracts={perception.leverage_headroom_contracts}. "
        "Follow the cognition pipeline exactly: Parse the event and market state, Quantify the action, then Generate the JSON. "
        "Return JSON only. The JSON must match the schema exactly. "
        "direction must be one of 1, 0, -1. size_score must stay within -3 to 3 and be direction-consistent. "
        "Use rationale to cite evidence from the inputs. "
        "Write memory_to_save as the sentence that should be fed into the next round."
    )
    user_payload = {
        "environment": environment.model_dump(),
        "event": event.model_dump(),
        "self": self_state.model_dump(),
        "perception": perception.model_dump(),
        "risk_tags": risk_tags,
    }
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=True)},
    ]


def build_decision_engine(adapter: LLMAdapter | None = None) -> DecisionEngine:
    if adapter is None:
        adapter = OpenAIAgentsSDKAdapter()
    return LLMDecisionEngine(adapter)


def _messages_to_agent_input(messages: List[dict[str, str]], schema: dict[str, Any]) -> tuple[str, str]:
    system_prompt = ""
    user_messages: List[str] = []

    for message in messages:
        if message["role"] == "system":
            system_prompt = message["content"]
        elif message["role"] == "user":
            user_messages.append(message["content"])

    user_messages.append(
        "Return only JSON that matches this schema exactly:\n" + json.dumps(schema, ensure_ascii=True)
    )
    return system_prompt, "\n\n".join(user_messages)


def _normalize_agent_output(output: Any) -> str:
    if isinstance(output, str):
        return output
    return json.dumps(output, ensure_ascii=True)


def _extract_json_text(raw_output: str) -> str:
    stripped = raw_output.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end >= start:
        return stripped[start : end + 1]
    return stripped


def _apply_document_overrides(
    *,
    role: str,
    event: Event,
    self_state: SelfState,
    environment: Environment,
    perception,
    risk_tags: List[str],
    action: AgentActionOutput,
) -> AgentActionOutput:
    updates: dict[str, Any] = {}

    if role == "CTA":
        updates["instrument_pref"] = "front"
        updates["horizon"] = "1w"
    elif role == "Global Macro PM":
        updates["horizon"] = "1m"
        if action.instrument_pref not in {"back", "options"}:
            updates["instrument_pref"] = "back"
    elif role == "Physical Hedger":
        updates["instrument_pref"] = "front"
        updates["horizon"] = "1d"
        updates["aggressiveness"] = max(action.aggressiveness, 0.9)
    elif role == "Options Dealer":
        updates["instrument_pref"] = "options"
        updates["horizon"] = "1d"
        updates["aggressiveness"] = max(action.aggressiveness, 0.85)
    elif role == "Spread Trader":
        updates["instrument_pref"] = "spread"
        updates["horizon"] = "3d"
        updates["aggressiveness"] = 0.4
        if action.direction > 0:
            updates["size_score"] = min(action.size_score, 1)
        elif action.direction < 0:
            updates["size_score"] = max(action.size_score, -1)
    elif role == "News HFT":
        updates["instrument_pref"] = "front"
        updates["horizon"] = "intraday"
        updates["aggressiveness"] = 1.0
        if action.direction > 0:
            updates["size_score"] = min(action.size_score, 2)
        elif action.direction < 0:
            updates["size_score"] = max(action.size_score, -2)

    if role == "Options Dealer" and environment.tail_risk_report.gamma_profile == "Short Gamma":
        updates["aggressiveness"] = 1.0
        if action.direction == 0:
            updates["direction"] = 1 if perception.headline_bias == "Bullish" else -1
        if int(updates.get("direction", action.direction)) > 0:
            updates["size_score"] = max(int(updates.get("size_score", action.size_score)), 2)
        elif int(updates.get("direction", action.direction)) < 0:
            updates["size_score"] = min(int(updates.get("size_score", action.size_score)), -2)
        updates["rationale"] = (
            action.rationale
            + " Short Gamma requires options-book hedging with maximum urgency."
        )[:600]

    if role == "Spread Trader" and perception.spread_zscore is not None and abs(perception.spread_zscore) >= 2.0:
        zscore = perception.spread_zscore
        updates.update(
            {
                "direction": -1 if zscore > 0 else 1,
                "size_score": -1 if zscore > 0 else 1,
                "aggressiveness": 0.4,
                "rationale": (
                    action.rationale
                    + f" Calendar spread z-score={zscore:.2f}, so the trade reverses toward historical mean."
                )[:600],
                "memory_to_save": (
                    action.memory_to_save
                    + f" Mean-reversion spread trade triggered at z-score {zscore:.2f}."
                )[:300],
            }
        )

    if role == "Physical Hedger":
        event_text = f"{event.headline} {event.body}".lower()
        is_supply_panic = any(
            keyword in event_text
            for keyword in ("supply disruption", "inventory low", "inventory shortage", "force majeure", "logistics")
        )
        if is_supply_panic:
            updates.update(
                {
                    "direction": 1,
                    "size_score": 3,
                    "aggressiveness": 1.0,
                    "rationale": (
                        action.rationale
                        + " Physical hedger panic-buys because supply security dominates price sensitivity."
                    )[:600],
                }
            )
        elif self_state.hedger_type == "producer" and environment.factor_snapshot.trend_score > 0.5:
            updates.update(
                {
                    "direction": -1,
                    "size_score": -1,
                    "aggressiveness": max(float(updates.get("aggressiveness", action.aggressiveness)), 0.9),
                    "rationale": (
                        action.rationale
                        + " Producer hedge sells into rising prices to lock margin."
                    )[:600],
                }
            )
        elif self_state.hedger_type == "consumer" and environment.factor_snapshot.trend_score > 0.5:
            updates.update(
                {
                    "direction": 1,
                    "size_score": 1,
                    "aggressiveness": max(float(updates.get("aggressiveness", action.aggressiveness)), 0.9),
                    "rationale": (
                        action.rationale
                        + " Consumer hedge buys into rising prices to lock procurement cost."
                    )[:600],
                }
            )

    if (
        perception.source_reliability == "Low"
        and role in {"CTA", "Global Macro PM", "Spread Trader"}
        and not action.is_risk_triggered
    ):
        updates["confidence"] = min(action.confidence, 0.4)
        if action.direction > 0:
            updates["size_score"] = min(int(updates.get("size_score", action.size_score)), 1)
        elif action.direction < 0:
            updates["size_score"] = max(int(updates.get("size_score", action.size_score)), -1)
        updates["rationale"] = (
            action.rationale
            + f" Source reliability is {perception.source_reliability}, so conviction is reduced."
        )[:600]

    if (
        environment.market_microstructure.order_book_depth == "Thin"
        and role in {"CTA", "Global Macro PM", "Spread Trader"}
        and not action.is_risk_triggered
        and "FORCED_CLOSE" not in risk_tags
    ):
        updates["aggressiveness"] = min(float(updates.get("aggressiveness", action.aggressiveness)), 0.7)
        updates["rationale"] = (
            updates.get("rationale", action.rationale)
            + " Thin order book requires less aggressive execution."
        )[:600]

    if (
        role == "News HFT"
        and environment.market_microstructure.bid_ask_spread >= WIDE_SPREAD_THRESHOLD
        and "FORCED_CLOSE" not in risk_tags
    ):
        updates.update(
            {
                "direction": 0,
                "size_score": 0,
                "aggressiveness": 0.0,
                "confidence": min(action.confidence, 0.15),
                "rationale": (
                    action.rationale
                    + " Bid-ask spread is too wide for News HFT, so the strategy exits and waits."
                )[:600],
                "memory_to_save": (
                    action.memory_to_save
                    + " Wide spread regime, HFT stood down."
                )[:300],
            }
        )

    if (
        role == "News HFT"
        and self_state.position != 0
        and self_state.last_action in {"Buy", "Sell"}
        and "FORCED_CLOSE" not in risk_tags
        and "CRITICAL_LOSS" not in risk_tags
    ):
        forced_direction = -1 if self_state.position > 0 else 1
        forced_size = -2 if self_state.position > 0 else 2
        updates.update(
            {
                "direction": forced_direction,
                "size_score": forced_size,
                "aggressiveness": 1.0,
                "horizon": "intraday",
                "rationale": (
                    action.rationale
                    + " News HFT holding period expired, so the position must be flattened."
                )[:600],
                "memory_to_save": (
                    action.memory_to_save
                    + " Flattened because HFT holding period expired."
                )[:300],
            }
        )

    if (
        self_state.consecutive_losses >= 3
        and role in {"CTA", "News HFT"}
        and not (role == "News HFT" and self_state.position != 0 and self_state.last_action in {"Buy", "Sell"})
        and not action.is_risk_triggered
        and "FORCED_CLOSE" not in risk_tags
    ):
        updates.update(
            {
                "direction": 0,
                "size_score": 0,
                "aggressiveness": min(float(updates.get("aggressiveness", action.aggressiveness)), 0.2),
                "confidence": min(action.confidence, 0.2),
                "rationale": (
                    action.rationale
                    + " Consecutive loss discipline triggered a temporary trading pause."
                )[:600],
                "memory_to_save": (
                    action.memory_to_save
                    + " Paused after consecutive losses."
                )[:300],
            }
        )

    if (
        perception.leverage_headroom_contracts == 0
        and action.direction == 1
        and self_state.position >= 0
        and not action.is_risk_triggered
    ):
        updates.update(
            {
                "direction": 0,
                "size_score": 0,
                "confidence": min(float(updates.get("confidence", action.confidence)), 0.2),
                "aggressiveness": min(float(updates.get("aggressiveness", action.aggressiveness)), 0.2),
                "rationale": (
                    updates.get("rationale", action.rationale)
                    + " Leverage headroom is exhausted, so new long exposure is blocked."
                )[:600],
                "memory_to_save": (
                    action.memory_to_save
                    + " New long blocked by leverage limit."
                )[:300],
            }
        )

    if (
        self_state.cash_level <= 0
        and action.direction == 1
        and self_state.position >= 0
        and not action.is_risk_triggered
    ):
        updates.update(
            {
                "direction": 0,
                "size_score": 0,
                "confidence": min(action.confidence, 0.2),
                "aggressiveness": min(float(updates.get("aggressiveness", action.aggressiveness)), 0.2),
                "rationale": (
                    action.rationale
                    + " Cash is depleted, so the strategy cannot initiate new long exposure."
                )[:600],
                "memory_to_save": (
                    action.memory_to_save
                    + " No cash available for new longs."
                )[:300],
            }
        )

    if ("CRITICAL_LOSS" in risk_tags or "FORCED_CLOSE" in risk_tags) and self_state.position != 0:
        forced_direction = -1 if self_state.position > 0 else 1
        forced_size = -3 if self_state.position > 0 else 3
        updates.update(
            {
                "direction": forced_direction,
                "size_score": forced_size,
                "aggressiveness": max(float(updates.get("aggressiveness", action.aggressiveness)), 0.81),
                "is_risk_triggered": True,
                "horizon": "Intraday",
                "rationale": (
                    action.rationale
                    + f" Risk override applied because tags={risk_tags} and position={self_state.position}."
                )[:600],
                "memory_to_save": (
                    action.memory_to_save
                    + f" Forced risk action under {','.join(risk_tags)}."
                )[:300],
            }
        )

    return AgentActionOutput.model_validate(action.model_dump() | updates)
