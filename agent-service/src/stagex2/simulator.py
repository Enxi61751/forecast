from __future__ import annotations

import os
from typing import Dict, Sequence

from .clearing import calibrate_clearing_parameters, load_clearing_calibration_observations, run_clearing
from .decision import LLMAdapter, build_decision_engine
from .execution import execute_orders, map_action_to_orders
from .perception import FORCED_CLOSE_MINUTES, derive_risk_tags
from .schemas import (
    AgentActionOutput,
    ClearingCalibrationObservation,
    ClearingInput,
    ClearingParameters,
    Environment,
    ExecutionState,
    MarketSimReport,
    MarketMicrostructure,
    SelfState,
    SimulationInput,
    StandardOrder,
    SessionInfo,
    TailRiskReport,
)

AGENT_ROLES = [
    "CTA",
    "Global Macro PM",
    "Physical Hedger",
    "Options Dealer",
    "Spread Trader",
    "News HFT",
]

PHASE_CYCLE = ["Open", "Mid-Day", "Close", "Overnight"]
MAX_TIME_TO_CLOSE = 390


def _next_phase(current_phase: str) -> str:
    try:
        idx = PHASE_CYCLE.index(current_phase)
    except ValueError:
        return PHASE_CYCLE[0]
    return PHASE_CYCLE[(idx + 1) % len(PHASE_CYCLE)]


def _build_agent_states(base_self_state: SelfState, agent_states: Dict[str, SelfState] | None) -> Dict[str, SelfState]:
    states = {
        role: base_self_state.model_copy(
            deep=True,
            update={
                "role": role,
            },
        )
        for role in AGENT_ROLES
    }
    if agent_states is not None:
        for role, state in agent_states.items():
            states[role] = state.model_copy(deep=True)
    return states


def _public_step_result(result: dict) -> dict:
    return {key: value for key, value in result.items() if key != "next_agent_states"}


def _resolve_clearing_parameters(
    clearing_parameters: ClearingParameters | None,
    calibration_observations: Sequence[ClearingCalibrationObservation] | None,
    calibration_file: str | None,
) -> ClearingParameters | None:
    if clearing_parameters is not None:
        return clearing_parameters
    if calibration_observations is not None:
        return calibrate_clearing_parameters(calibration_observations)

    resolved_file = calibration_file or os.getenv("STAGEX2_CALIBRATION_FILE")
    if resolved_file:
        observations = load_clearing_calibration_observations(resolved_file)
        return calibrate_clearing_parameters(observations)
    return None


def feedback_environment(
    environment: Environment,
    market_sim_report: MarketSimReport,
) -> Environment:
    next_time_to_close = max(0, environment.session_info.time_to_close - FORCED_CLOSE_MINUTES)
    if next_time_to_close == 0:
        next_phase = _next_phase(environment.session_info.phase)
        next_time_to_close = MAX_TIME_TO_CLOSE if next_phase == "Open" else environment.session_info.time_to_close
    else:
        next_phase = environment.session_info.phase

    return Environment(
        factor_snapshot=environment.factor_snapshot.model_copy(update={"current_price": market_sim_report.new_price}),
        tail_risk_report=TailRiskReport(
            gamma_profile=market_sim_report.new_gamma_profile,  # type: ignore[arg-type]
            liquidity_stress=market_sim_report.liquidity_stress,
        ),
        market_microstructure=MarketMicrostructure(
            bid_ask_spread=market_sim_report.updated_bid_ask_spread,
            order_book_depth=market_sim_report.updated_order_book_depth,  # type: ignore[arg-type]
            spread_bid_ask_spread=market_sim_report.updated_spread_bid_ask_spread,
            spread_order_book_depth=market_sim_report.updated_spread_order_book_depth,  # type: ignore[arg-type]
            options_bid_ask_spread=market_sim_report.updated_options_bid_ask_spread,
            options_order_book_depth=market_sim_report.updated_options_order_book_depth,  # type: ignore[arg-type]
        ),
        session_info=SessionInfo(
            phase=next_phase,  # type: ignore[arg-type]
            time_to_close=next_time_to_close,
        ),
    )


def _update_agent_self_state(
    self_state: SelfState,
    executed_orders: Sequence[StandardOrder],
    action: AgentActionOutput,
    new_price: float,
    current_price: float,
) -> SelfState:
    buy_quantity = sum(order.quantity for order in executed_orders if order.side == "BUY")
    sell_quantity = sum(order.quantity for order in executed_orders if order.side == "SELL")
    position_delta = buy_quantity - sell_quantity

    if position_delta > 0:
        last_direction = "Buy"
    elif position_delta < 0:
        last_direction = "Sell"
    else:
        last_direction = "Hold"

    mark_to_market_pnl = self_state.unrealized_pnl + self_state.position * (new_price - current_price)
    next_position = self_state.position + position_delta
    next_unrealized_pnl = mark_to_market_pnl
    next_cash_level = max(0.0, self_state.cash_level - buy_quantity * current_price + sell_quantity * current_price)
    next_unrealized_pnl_pct = (
        next_unrealized_pnl / next_cash_level if next_cash_level > 0 else self_state.unrealized_pnl_pct
    )

    return self_state.model_copy(
        update={
            "position": next_position,
            "unrealized_pnl_pct": next_unrealized_pnl_pct,
            "unrealized_pnl": next_unrealized_pnl,
            "cash_level": next_cash_level,
            "last_action": last_direction,
            "consecutive_losses": self_state.consecutive_losses + 1 if next_unrealized_pnl_pct < 0 else 0,
            "view_history": action.memory_to_save or self_state.view_history,
        }
    )


def run_single_step(
    simulation_input: SimulationInput,
    current_price: float,
    current_volatility: float,
    dealer_inventory: int,
    llm_adapter: LLMAdapter | None = None,
    max_position_limit: int = 500,
    seed: int = 7,
    clearing_parameters: ClearingParameters | None = None,
    calibration_observations: Sequence[ClearingCalibrationObservation] | None = None,
    calibration_file: str | None = None,
    agent_states: Dict[str, SelfState] | None = None,
    execution_state: ExecutionState | None = None,
):
    return _public_step_result(
        _run_single_step_internal(
            simulation_input,
            current_price,
            current_volatility,
            dealer_inventory,
            llm_adapter=llm_adapter,
            max_position_limit=max_position_limit,
            seed=seed,
            clearing_parameters=clearing_parameters,
            calibration_observations=calibration_observations,
            calibration_file=calibration_file,
            agent_states=agent_states,
            execution_state=execution_state,
        )
    )


def _run_single_step_internal(
    simulation_input: SimulationInput,
    current_price: float,
    current_volatility: float,
    dealer_inventory: int,
    llm_adapter: LLMAdapter | None = None,
    max_position_limit: int = 500,
    seed: int = 7,
    agent_states: Dict[str, SelfState] | None = None,
    execution_state: ExecutionState | None = None,
    clearing_parameters: ClearingParameters | None = None,
    calibration_observations: Sequence[ClearingCalibrationObservation] | None = None,
    calibration_file: str | None = None,
):
    current_environment = simulation_input.environment.model_copy(
        update={
            "factor_snapshot": simulation_input.environment.factor_snapshot.model_copy(
                update={"current_price": current_price}
            )
        }
    )
    current_input = simulation_input.model_copy(update={"environment": current_environment})
    decision_engine = build_decision_engine(llm_adapter)
    current_agent_states = _build_agent_states(current_input.self_state, agent_states)
    agent_actions = []
    submitted_orders = []
    current_execution_state = execution_state.model_copy(deep=True) if execution_state is not None else ExecutionState()
    order_sequence = current_execution_state.next_order_sequence

    for role in AGENT_ROLES:
        self_state = current_agent_states[role]
        risk_tags = derive_risk_tags(
            environment=current_input.environment,
            self_state=self_state,
            assumed_horizon=decision_engine.default_horizon_for_role(role),
        )
        action = decision_engine.decide(
            event=current_input.event,
            environment=current_input.environment,
            self_state=self_state,
            risk_tags=risk_tags,
        )
        agent_actions.append(action)
        orders_for_agent, order_sequence = map_action_to_orders(
                action,
                agent_id=role,
                self_state=self_state,
                current_price=current_price,
                environment=current_input.environment,
                order_sequence=order_sequence,
                max_position_limit=max_position_limit,
        )
        submitted_orders.extend(orders_for_agent)

    current_execution_state = current_execution_state.model_copy(update={"next_order_sequence": order_sequence})
    execution_report, next_execution_state = execute_orders(
        submitted_orders,
        current_execution_state,
        current_input.environment,
        seed=seed,
    )
    order_flow = execution_report.executed_orders
    clearing_parameters = _resolve_clearing_parameters(
        clearing_parameters,
        calibration_observations,
        calibration_file,
    )

    market_sim_report, dealer_new_inventory = run_clearing(
        ClearingInput(
            order_flow=order_flow,
            current_price=current_price,
            current_liquidity_stress=current_input.environment.tail_risk_report.liquidity_stress,
            current_bid_ask_spread=current_input.environment.market_microstructure.bid_ask_spread,
            current_spread_bid_ask_spread=current_input.environment.market_microstructure.spread_bid_ask_spread,
            current_options_bid_ask_spread=current_input.environment.market_microstructure.options_bid_ask_spread,
            current_volatility=current_volatility,
            dealer_inventory=dealer_inventory,
        ),
        seed=seed,
        parameters=clearing_parameters,
    )
    next_environment = feedback_environment(current_input.environment, market_sim_report)
    next_agent_states = {
        role: _update_agent_self_state(
            current_agent_states[role],
            [order for order in order_flow if order.agent_id == role],
            action,
            market_sim_report.new_price,
            current_price,
        )
        for role, action in zip(AGENT_ROLES, agent_actions)
    }
    selected_role = current_input.self_state.role if current_input.self_state.role in next_agent_states else AGENT_ROLES[0]
    next_self_state = next_agent_states[selected_role]
    return {
        "agent_actions": agent_actions,
        "submitted_orders": submitted_orders,
        "order_flow": order_flow,
        "execution_report": execution_report,
        "market_sim_report": market_sim_report,
        "next_environment": next_environment,
        "next_self": next_self_state,
        "next_agent_states": next_agent_states,
        "next_execution_state": next_execution_state.model_copy(update={"next_order_sequence": order_sequence}),
        "next_current_price": market_sim_report.new_price,
        "next_current_volatility": market_sim_report.new_volatility,
        "next_dealer_inventory": dealer_new_inventory,
    }


def run_multi_step(
    simulation_input: SimulationInput,
    current_price: float,
    current_volatility: float,
    dealer_inventory: int,
    llm_adapter: LLMAdapter | None = None,
    steps: int = 10,
    max_position_limit: int = 500,
    seed: int = 7,
    clearing_parameters: ClearingParameters | None = None,
    calibration_observations: Sequence[ClearingCalibrationObservation] | None = None,
    calibration_file: str | None = None,
    initial_agent_states: Dict[str, SelfState] | None = None,
    initial_execution_state: ExecutionState | None = None,
):
    current_input = simulation_input.model_copy(deep=True)
    history = []
    price = current_price
    volatility = current_volatility
    inventory = dealer_inventory
    agent_states: Dict[str, SelfState] | None = (
        {role: state.model_copy(deep=True) for role, state in initial_agent_states.items()}
        if initial_agent_states is not None
        else None
    )
    execution_state = initial_execution_state.model_copy(deep=True) if initial_execution_state is not None else None
    clearing_parameters = _resolve_clearing_parameters(
        clearing_parameters,
        calibration_observations,
        calibration_file,
    )

    for offset in range(steps):
        result = _run_single_step_internal(
            current_input,
            price,
            volatility,
            inventory,
            llm_adapter=llm_adapter,
            max_position_limit=max_position_limit,
            seed=seed + offset,
            agent_states=agent_states,
            execution_state=execution_state,
            clearing_parameters=clearing_parameters,
            calibration_observations=calibration_observations,
            calibration_file=calibration_file,
        )
        history.append(_public_step_result(result))
        price = result["next_current_price"]
        volatility = result["next_current_volatility"]
        inventory = result["next_dealer_inventory"]
        agent_states = result["next_agent_states"]
        execution_state = result["next_execution_state"]
        current_input = current_input.model_copy(
            update={
                "environment": result["next_environment"],
                "self_state": result["next_self"],
            }
        )

    return {
        "steps": history,
        "final_environment": current_input.environment,
        "final_self": current_input.self_state,
        "final_current_price": price,
        "final_current_volatility": volatility,
        "final_dealer_inventory": inventory,
        "final_execution_state": execution_state,
    }
