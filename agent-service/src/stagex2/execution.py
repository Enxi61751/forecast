from __future__ import annotations

import math
import random
from typing import Iterable

from .schemas import (
    AgentActionOutput,
    BookDepth,
    Environment,
    ExecutionReport,
    ExecutionState,
    SelfState,
    StandardOrder,
)

TRADING_MINUTES_PER_STEP = 15
TRADING_MINUTES_PER_DAY = 390
BOOK_LIQUIDITY_FACTOR = {
    "front": 1.0,
    "spread": 0.8,
    "options": 0.6,
}
FILL_RATIO_MATRIX = {
    "MARKET": {"Deep": 1.0, "Normal": 0.9, "Thin": 0.65},
    "LIMIT_AGG": {"Deep": 0.85, "Normal": 0.65, "Thin": 0.4},
    "LIMIT_PASS": {"Deep": 0.55, "Normal": 0.3, "Thin": 0.12},
}


def _effective_abs_position_limit(
    self_state: SelfState,
    current_price: float,
    max_position_limit: int,
) -> int:
    if current_price <= 0 or self_state.cash_level <= 0 or self_state.max_leverage <= 0:
        return 0
    leverage_cap = int((self_state.cash_level * self_state.max_leverage) / current_price)
    return max(0, min(max_position_limit, leverage_cap))


def _cap_quantity_by_position_constraints(
    quantity: int,
    direction: int,
    current_position: float,
    abs_position_limit: int,
) -> int:
    upper_bound = float(abs_position_limit)
    lower_bound = -float(abs_position_limit)

    if direction > 0:
        allowed_delta = max(0.0, min(float(quantity), upper_bound - current_position))
        return int(round(allowed_delta))
    if direction < 0:
        allowed_delta = min(0.0, max(-float(quantity), lower_bound - current_position))
        return int(round(abs(allowed_delta)))
    return 0


def _resolve_book(action: AgentActionOutput) -> str:
    if action.instrument_pref in {"front", "spread", "options"}:
        return action.instrument_pref
    return "front"


def _resolve_book_state(environment: Environment, book: str) -> tuple[float, BookDepth]:
    micro = environment.market_microstructure
    if book == "spread":
        return (
            micro.spread_bid_ask_spread or micro.bid_ask_spread,
            micro.spread_order_book_depth or micro.order_book_depth,
        )
    if book == "options":
        return (
            micro.options_bid_ask_spread or micro.bid_ask_spread,
            micro.options_order_book_depth or micro.order_book_depth,
        )
    return micro.bid_ask_spread, micro.order_book_depth


def _ttl_steps_for_horizon(horizon: str, time_to_close: int) -> int:
    if horizon in {"Intraday", "intraday"}:
        return max(1, math.ceil(max(time_to_close, TRADING_MINUTES_PER_STEP) / TRADING_MINUTES_PER_STEP))
    if horizon == "1d":
        return math.ceil(TRADING_MINUTES_PER_DAY / TRADING_MINUTES_PER_STEP)
    if horizon == "3d":
        return 3 * math.ceil(TRADING_MINUTES_PER_DAY / TRADING_MINUTES_PER_STEP)
    if horizon == "1w":
        return 5 * math.ceil(TRADING_MINUTES_PER_DAY / TRADING_MINUTES_PER_STEP)
    if horizon == "1m":
        return 20 * math.ceil(TRADING_MINUTES_PER_DAY / TRADING_MINUTES_PER_STEP)
    return 1


def _split_quantity(total_quantity: int, parts: int) -> list[int]:
    if parts <= 1 or total_quantity <= 0:
        return [max(0, total_quantity)]
    base = total_quantity // parts
    remainder = total_quantity % parts
    return [base + (1 if index < remainder else 0) for index in range(parts)]


def _child_order_count(quantity: int, depth: BookDepth) -> int:
    if depth != "Thin" or quantity <= 1:
        return 1
    return min(4, max(2, math.ceil(quantity / 25)))


def map_action_to_orders(
    action: AgentActionOutput,
    agent_id: str,
    self_state: SelfState,
    current_price: float,
    environment: Environment,
    order_sequence: int,
    max_position_limit: int = 500,
) -> tuple[list[StandardOrder], int]:
    abs_position_limit = _effective_abs_position_limit(self_state, current_price, max_position_limit)
    limit_basis = abs_position_limit
    if action.is_risk_triggered:
        limit_basis = max(abs_position_limit, int(round(abs(self_state.position))))

    raw_qty = limit_basis * (abs(action.size_score) / 3.0) * action.confidence
    quantity = int(round(raw_qty))
    side_map = {1: "BUY", -1: "SELL", 0: "NONE"}
    side = side_map[action.direction]
    book = _resolve_book(action)
    spread, depth = _resolve_book_state(environment, book)
    ttl_steps = _ttl_steps_for_horizon(action.horizon, environment.session_info.time_to_close)

    if action.is_risk_triggered:
        order_type = "MARKET"
        price_strategy = "Forced Liquidation"
        quantity = int(round(limit_basis * (abs(action.size_score) / 3.0)))
    elif action.aggressiveness > 0.8:
        order_type = "MARKET"
        price_strategy = "Market Take"
    elif action.aggressiveness > 0.4:
        order_type = "LIMIT"
        price_strategy = "Best Bid/Ask (Aggressive)"
    else:
        order_type = "LIMIT"
        price_strategy = "Mid-Price (Passive)"

    if action.direction == 0:
        quantity = 0
    else:
        quantity = _cap_quantity_by_position_constraints(
            quantity,
            action.direction,
            self_state.position,
            abs_position_limit,
        )

    if quantity <= 0 or side == "NONE":
        return [], order_sequence

    if depth == "Thin" and not action.is_risk_triggered:
        order_type = "LIMIT"
        price_strategy = "Layered Child Orders"

    child_count = _child_order_count(quantity, depth) if depth == "Thin" and not action.is_risk_triggered else 1
    child_quantities = _split_quantity(quantity, child_count)
    parent_order_id = f"{agent_id}-{order_sequence}" if child_count > 1 else None
    created_orders: list[StandardOrder] = []

    for index, child_quantity in enumerate(child_quantities):
        if child_quantity <= 0:
            continue
        order_id = f"{agent_id}-{order_sequence + index}"
        created_orders.append(
            StandardOrder(
                order_id=order_id,
                parent_order_id=parent_order_id,
                agent_id=agent_id,
                book=book,  # type: ignore[arg-type]
                symbol=f"OIL_{book.upper()}",
                side=side,  # type: ignore[arg-type]
                order_type=order_type,  # type: ignore[arg-type]
                quantity=child_quantity,
                filled_quantity=0,
                remaining_quantity=child_quantity,
                ttl_steps=max(1, ttl_steps - index) if child_count > 1 else ttl_steps,
                horizon=action.horizon,
                status="WORKING",
                aggressiveness=min(action.aggressiveness, 0.7) if depth == "Thin" and not action.is_risk_triggered else action.aggressiveness,
                price_strategy=price_strategy if child_count == 1 else f"{price_strategy} #{index + 1}",
                reason=(
                    action.rationale
                    + (
                        f" Book spread={spread:.4f}, depth={depth}, split into child order."
                        if child_count > 1
                        else ""
                    )
                )[:600],
            )
        )

    return created_orders, order_sequence + max(len(created_orders), 1)


def _fill_profile_key(order: StandardOrder) -> str:
    if order.order_type == "MARKET":
        return "MARKET"
    if order.aggressiveness > 0.4:
        return "LIMIT_AGG"
    return "LIMIT_PASS"


def _simulate_fill_quantity(
    order: StandardOrder,
    environment: Environment,
    rng: random.Random,
) -> int:
    spread, depth = _resolve_book_state(environment, order.book)
    profile_key = _fill_profile_key(order)
    base_ratio = FILL_RATIO_MATRIX[profile_key][depth]
    book_factor = BOOK_LIQUIDITY_FACTOR[order.book]
    spread_factor = 1.0 / (1.0 + max(0.0, spread))
    jitter = rng.uniform(0.9, 1.1)
    fill_ratio = max(0.0, min(1.0, base_ratio * book_factor * spread_factor * jitter))
    filled = int(math.floor(order.remaining_quantity * fill_ratio))

    if filled == 0 and order.remaining_quantity > 0:
        if order.order_type == "MARKET":
            filled = 1
        elif fill_ratio >= 0.25:
            filled = 1
    return min(order.remaining_quantity, filled)


def execute_orders(
    submitted_orders: Iterable[StandardOrder],
    execution_state: ExecutionState | None,
    environment: Environment,
    seed: int = 7,
) -> tuple[ExecutionReport, ExecutionState]:
    rng = random.Random(seed)
    prior_orders = execution_state.working_orders if execution_state is not None else []
    active_orders = [order.model_copy(deep=True) for order in prior_orders] + [
        order.model_copy(deep=True) for order in submitted_orders
    ]

    executed_orders: list[StandardOrder] = []
    cancelled_orders: list[StandardOrder] = []
    expired_orders: list[StandardOrder] = []
    next_working_orders: list[StandardOrder] = []

    for order in active_orders:
        if order.remaining_quantity <= 0 or order.side == "NONE":
            continue

        filled_now = _simulate_fill_quantity(order, environment, rng)
        remaining_after_fill = max(0, order.remaining_quantity - filled_now)
        next_ttl = max(0, order.ttl_steps - 1)

        if filled_now > 0:
            executed_orders.append(
                order.model_copy(
                    update={
                        "quantity": filled_now,
                        "filled_quantity": filled_now,
                        "remaining_quantity": 0,
                        "status": "FILLED" if remaining_after_fill == 0 else "PARTIAL",
                    }
                )
            )

        if remaining_after_fill <= 0:
            continue

        residual_order = order.model_copy(
            update={
                "filled_quantity": order.filled_quantity + filled_now,
                "remaining_quantity": remaining_after_fill,
                "ttl_steps": next_ttl,
                "status": "PARTIAL" if filled_now > 0 else "WORKING",
            }
        )

        if order.order_type == "MARKET":
            cancelled_orders.append(residual_order.model_copy(update={"status": "CANCELLED"}))
        elif next_ttl <= 0:
            expired_orders.append(residual_order.model_copy(update={"status": "EXPIRED"}))
        else:
            next_working_orders.append(residual_order)

    report = ExecutionReport(
        submitted_orders=[order.model_copy(deep=True) for order in submitted_orders],
        executed_orders=executed_orders,
        cancelled_orders=cancelled_orders,
        expired_orders=expired_orders,
        working_orders=next_working_orders,
    )
    next_state = ExecutionState(
        working_orders=next_working_orders,
        next_order_sequence=(execution_state.next_order_sequence if execution_state is not None else 1),
    )
    return report, next_state
