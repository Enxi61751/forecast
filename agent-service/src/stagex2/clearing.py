from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from typing import Sequence

from .schemas import (
    ClearingCalibrationObservation,
    ClearingInput,
    ClearingParameters,
    MarketSimReport,
)

LAMBDA_BASE = 0.0001
ALPHA_RECOVERY = 0.02
BETA_CONSUMPTION = 0.0002
NOISE_SCALE = 0.1
VOLATILITY_SENSITIVITY = 2.0
SHORT_GAMMA_INVENTORY_THRESHOLD = -5000
LONG_GAMMA_INVENTORY_THRESHOLD = 5000
SHORT_GAMMA_VOL_MULTIPLIER = 1.5
MIN_PRICE = 0.01
SPREAD_WIDENING_MULTIPLIER = 0.5
TEMPORARY_IMPACT_MULTIPLIER = 0.05
OPTIONS_DELTA_EQUIVALENT = 0.5
DEFAULT_CLEARING_PARAMETERS = ClearingParameters(
    lambda_base=LAMBDA_BASE,
    alpha_recovery=ALPHA_RECOVERY,
    beta_consumption=BETA_CONSUMPTION,
    noise_scale=NOISE_SCALE,
    volatility_sensitivity=VOLATILITY_SENSITIVITY,
    short_gamma_inventory_threshold=SHORT_GAMMA_INVENTORY_THRESHOLD,
    long_gamma_inventory_threshold=LONG_GAMMA_INVENTORY_THRESHOLD,
    short_gamma_vol_multiplier=SHORT_GAMMA_VOL_MULTIPLIER,
    spread_widening_multiplier=SPREAD_WIDENING_MULTIPLIER,
    temporary_impact_multiplier=TEMPORARY_IMPACT_MULTIPLIER,
)


def compute_dynamic_lambda(lambda_base: float, liquidity_stress: float) -> float:
    return lambda_base * (1.0 + liquidity_stress**2)


def _signed_quantity(side: str, quantity: int) -> int:
    if side == "BUY":
        return quantity
    if side == "SELL":
        return -quantity
    return 0


def _impact_weight(order_type: str, aggressiveness: float) -> float:
    if order_type == "MARKET":
        return 1.0
    if aggressiveness > 0.4:
        return 0.7
    return 0.4


def _urgency_pressure(order_flow, total_volume: int | float) -> float:
    if total_volume <= 0:
        return 0.0
    return sum(
        order.quantity * order.aggressiveness
        for order in order_flow
        if order.side != "NONE"
    ) / total_volume


def _temporary_impact(
    current_bid_ask_spread: float,
    signed_flow: float,
    total_volume: int,
    order_flow,
    multiplier: float,
) -> float:
    if total_volume <= 0 or signed_flow == 0:
        return 0.0

    urgency_pressure = _urgency_pressure(order_flow, total_volume)
    direction = 1.0 if signed_flow > 0 else -1.0
    return direction * current_bid_ask_spread * urgency_pressure * multiplier


def _effective_flow_for_books(order_flow, books: set[str] | None = None) -> float:
    return sum(
        _signed_quantity(order.side, order.quantity) * _impact_weight(order.order_type, order.aggressiveness)
        for order in order_flow
        if books is None or order.book in books
    )


def _raw_flow_for_books(order_flow, books: set[str] | None = None) -> int:
    return sum(
        _signed_quantity(order.side, order.quantity)
        for order in order_flow
        if books is None or order.book in books
    )


def _liquidity_consumption_for_books(order_flow, books: set[str] | None = None) -> float:
    return sum(
        order.quantity * _impact_weight(order.order_type, order.aggressiveness)
        for order in order_flow
        if order.side != "NONE" and (books is None or order.book in books)
    )


def _book_depth_from_stress(liquidity_stress: float) -> str:
    if liquidity_stress >= 0.8:
        return "Thin"
    if liquidity_stress >= 0.4:
        return "Normal"
    return "Deep"


def _updated_book_spread(
    base_spread: float,
    liquidity_stress: float,
    book_consumption: float,
    total_consumption: float,
    spread_widening_multiplier: float,
    book_multiplier: float = 1.0,
) -> float:
    consumption_share = 0.0 if total_consumption <= 0 else book_consumption / total_consumption
    return max(
        MIN_PRICE,
        base_spread
        * (
            1.0
            + liquidity_stress * spread_widening_multiplier
            + consumption_share * spread_widening_multiplier * book_multiplier
        ),
    )


def _regress_no_intercept(x_values: Sequence[float], y_values: Sequence[float]) -> float:
    denominator = sum(x * x for x in x_values)
    if denominator <= 0:
        return 0.0
    return sum(x * y for x, y in zip(x_values, y_values)) / denominator


def _regress_with_intercept(x_values: Sequence[float], y_values: Sequence[float]) -> tuple[float, float]:
    n = len(x_values)
    if n == 0:
        return 0.0, 0.0

    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xx = sum(x * x for x in x_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    denominator = n * sum_xx - sum_x * sum_x
    if denominator == 0:
        return sum_y / n, 0.0

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    return intercept, slope


def _regress_two_feature_no_intercept(
    feature_one: Sequence[float],
    feature_two: Sequence[float],
    target: Sequence[float],
) -> tuple[float, float]:
    s11 = sum(x1 * x1 for x1 in feature_one)
    s22 = sum(x2 * x2 for x2 in feature_two)
    s12 = sum(x1 * x2 for x1, x2 in zip(feature_one, feature_two))
    t1 = sum(x1 * y for x1, y in zip(feature_one, target))
    t2 = sum(x2 * y for x2, y in zip(feature_two, target))
    determinant = s11 * s22 - s12 * s12
    if determinant == 0:
        return _regress_no_intercept(feature_one, target), _regress_no_intercept(feature_two, target)

    coefficient_one = (t1 * s22 - t2 * s12) / determinant
    coefficient_two = (s11 * t2 - s12 * t1) / determinant
    return coefficient_one, coefficient_two


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def _positive_or_default(value: float, default: float) -> float:
    return value if value > 0 else default


def load_clearing_calibration_observations(path: str | Path) -> list[ClearingCalibrationObservation]:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Calibration observations file not found: {source_path}")

    if source_path.suffix.lower() == ".json":
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Calibration JSON must be a list of observations.")
        return [ClearingCalibrationObservation.model_validate(item) for item in payload]

    if source_path.suffix.lower() in {".csv", ".tsv"}:
        delimiter = "\t" if source_path.suffix.lower() == ".tsv" else ","
        with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            return [ClearingCalibrationObservation.model_validate(row) for row in reader]

    raise ValueError("Unsupported calibration file format. Use JSON, CSV, or TSV.")


def calibrate_clearing_parameters(
    observations: Sequence[ClearingCalibrationObservation],
) -> ClearingParameters:
    if not observations:
        raise ValueError("At least one calibration observation is required.")

    price_feature = [
        (1.0 + observation.liquidity_stress**2) * observation.effective_net_flow
        for observation in observations
    ]
    temporary_feature = [
        observation.current_bid_ask_spread
        * observation.urgency_pressure
        * (1.0 if observation.effective_net_flow >= 0 else -1.0)
        for observation in observations
    ]
    price_target = [observation.price_change for observation in observations]
    lambda_base, temporary_impact_multiplier = _regress_two_feature_no_intercept(
        price_feature,
        temporary_feature,
        price_target,
    )

    liquidity_target = [
        observation.next_liquidity_stress - observation.liquidity_stress
        for observation in observations
    ]
    alpha_recovery, liquidity_slope = _regress_with_intercept(
        [observation.total_volume for observation in observations],
        liquidity_target,
    )
    beta_consumption = max(0.0, -liquidity_slope)

    volatility_feature: list[float] = []
    volatility_target: list[float] = []
    short_gamma_ratios: list[float] = []
    for observation in observations:
        if observation.current_volatility <= 0 or observation.current_price <= 0:
            continue
        price_change_pct = abs(observation.price_change / observation.current_price)
        realized_vol_ratio = observation.next_volatility / observation.current_volatility
        if observation.next_gamma_profile == "Short Gamma":
            short_gamma_ratios.append(max(1.0, realized_vol_ratio))
            continue
        volatility_feature.append(price_change_pct)
        volatility_target.append(max(0.0, realized_vol_ratio - 1.0))

    volatility_sensitivity = _regress_no_intercept(volatility_feature, volatility_target)
    if volatility_sensitivity <= 0:
        volatility_sensitivity = DEFAULT_CLEARING_PARAMETERS.volatility_sensitivity

    if short_gamma_ratios:
        short_gamma_vol_multiplier = max(1.0, sum(short_gamma_ratios) / len(short_gamma_ratios))
    else:
        short_gamma_vol_multiplier = DEFAULT_CLEARING_PARAMETERS.short_gamma_vol_multiplier

    spread_feature = [observation.next_liquidity_stress for observation in observations]
    spread_target = [
        max(0.0, observation.updated_bid_ask_spread / observation.current_bid_ask_spread - 1.0)
        for observation in observations
    ]
    spread_widening_multiplier = _regress_no_intercept(spread_feature, spread_target)

    residuals = [
        observation.price_change - lambda_base * x1 - temporary_impact_multiplier * x2
        for observation, x1, x2 in zip(observations, price_feature, temporary_feature)
    ]
    normalized_residuals = [
        residual / observation.current_volatility
        for observation, residual in zip(observations, residuals)
        if observation.current_volatility > 0
    ]
    noise_scale = _rms(normalized_residuals)

    return ClearingParameters(
        lambda_base=_positive_or_default(lambda_base, DEFAULT_CLEARING_PARAMETERS.lambda_base),
        alpha_recovery=_positive_or_default(alpha_recovery, DEFAULT_CLEARING_PARAMETERS.alpha_recovery),
        beta_consumption=_positive_or_default(beta_consumption, DEFAULT_CLEARING_PARAMETERS.beta_consumption),
        noise_scale=_positive_or_default(noise_scale, DEFAULT_CLEARING_PARAMETERS.noise_scale),
        volatility_sensitivity=volatility_sensitivity,
        short_gamma_inventory_threshold=DEFAULT_CLEARING_PARAMETERS.short_gamma_inventory_threshold,
        long_gamma_inventory_threshold=DEFAULT_CLEARING_PARAMETERS.long_gamma_inventory_threshold,
        short_gamma_vol_multiplier=short_gamma_vol_multiplier,
        spread_widening_multiplier=_positive_or_default(
            spread_widening_multiplier,
            DEFAULT_CLEARING_PARAMETERS.spread_widening_multiplier,
        ),
        temporary_impact_multiplier=_positive_or_default(
            temporary_impact_multiplier,
            DEFAULT_CLEARING_PARAMETERS.temporary_impact_multiplier,
        ),
    )


def run_clearing(
    clearing_input: ClearingInput,
    seed: int = 7,
    parameters: ClearingParameters | None = None,
) -> tuple[MarketSimReport, int]:
    params = parameters or DEFAULT_CLEARING_PARAMETERS
    rng = random.Random(seed)

    buy_volume = sum(order.quantity for order in clearing_input.order_flow if order.side == "BUY")
    sell_volume = sum(order.quantity for order in clearing_input.order_flow if order.side == "SELL")
    total_volume = buy_volume + sell_volume
    front_effective_flow = _effective_flow_for_books(clearing_input.order_flow, {"front"})
    spread_effective_flow = _effective_flow_for_books(clearing_input.order_flow, {"spread"})
    options_effective_flow = _effective_flow_for_books(clearing_input.order_flow, {"options"})
    effective_net_flow = front_effective_flow + spread_effective_flow + options_effective_flow * OPTIONS_DELTA_EQUIVALENT
    front_raw_flow = _raw_flow_for_books(clearing_input.order_flow, {"front"})
    spread_raw_flow = _raw_flow_for_books(clearing_input.order_flow, {"spread"})
    options_raw_flow = _raw_flow_for_books(clearing_input.order_flow, {"options"})
    net_flow = front_raw_flow + spread_raw_flow + int(round(options_raw_flow * OPTIONS_DELTA_EQUIVALENT))
    front_consumption = _liquidity_consumption_for_books(clearing_input.order_flow, {"front"})
    spread_consumption = _liquidity_consumption_for_books(clearing_input.order_flow, {"spread"})
    options_consumption = _liquidity_consumption_for_books(clearing_input.order_flow, {"options"})
    liquidity_consumption = front_consumption + spread_consumption + options_consumption
    temporary_impact = _temporary_impact(
        clearing_input.current_bid_ask_spread,
        effective_net_flow,
        total_volume,
        clearing_input.order_flow,
        params.temporary_impact_multiplier,
    )

    dynamic_lambda = compute_dynamic_lambda(params.lambda_base, clearing_input.current_liquidity_stress)
    noise = rng.gauss(0.0, clearing_input.current_volatility * params.noise_scale)
    delta_price = dynamic_lambda * effective_net_flow + temporary_impact + noise
    new_price = max(MIN_PRICE, clearing_input.current_price + delta_price)

    new_liquidity_stress = (
        clearing_input.current_liquidity_stress
        + params.alpha_recovery
        - params.beta_consumption * liquidity_consumption
    )
    new_liquidity_stress = max(0.0, min(1.0, new_liquidity_stress))

    dealer_new_inventory = clearing_input.dealer_inventory - net_flow
    if dealer_new_inventory <= params.short_gamma_inventory_threshold:
        new_gamma_profile = "Short Gamma"
    elif dealer_new_inventory >= params.long_gamma_inventory_threshold:
        new_gamma_profile = "Long Gamma"
    else:
        new_gamma_profile = "Neutral"

    price_change_pct = (
        (new_price - clearing_input.current_price) / clearing_input.current_price
        if clearing_input.current_price > 0
        else 0.0
    )
    new_volatility = clearing_input.current_volatility * (1.0 + abs(price_change_pct) * params.volatility_sensitivity)
    if new_gamma_profile == "Short Gamma":
        new_volatility *= params.short_gamma_vol_multiplier

    updated_bid_ask_spread = _updated_book_spread(
        clearing_input.current_bid_ask_spread,
        new_liquidity_stress,
        front_consumption,
        liquidity_consumption,
        params.spread_widening_multiplier,
        book_multiplier=1.0,
    )
    updated_spread_bid_ask_spread = _updated_book_spread(
        clearing_input.current_spread_bid_ask_spread or clearing_input.current_bid_ask_spread,
        new_liquidity_stress,
        spread_consumption,
        liquidity_consumption,
        params.spread_widening_multiplier,
        book_multiplier=0.8,
    )
    updated_options_bid_ask_spread = _updated_book_spread(
        clearing_input.current_options_bid_ask_spread or clearing_input.current_bid_ask_spread,
        new_liquidity_stress,
        options_consumption,
        liquidity_consumption,
        params.spread_widening_multiplier,
        book_multiplier=1.25,
    )
    updated_order_book_depth = _book_depth_from_stress(
        min(1.0, new_liquidity_stress + (front_consumption / max(total_volume, 1)))
    )
    updated_spread_order_book_depth = _book_depth_from_stress(
        min(1.0, new_liquidity_stress + (spread_consumption / max(total_volume, 1)))
    )
    updated_options_order_book_depth = _book_depth_from_stress(
        min(1.0, new_liquidity_stress + (options_consumption / max(total_volume, 1)))
    )

    report = MarketSimReport(
        simulated_flow_pressure=dynamic_lambda * effective_net_flow + temporary_impact,
        liquidity_stress=new_liquidity_stress,
        gamma_squeeze_risk=min(
            1.0,
            (abs(dealer_new_inventory) + abs(options_raw_flow) * OPTIONS_DELTA_EQUIVALENT)
            / max(abs(params.short_gamma_inventory_threshold), 1),
        ),
        spread_pressure=dynamic_lambda * spread_effective_flow,
        new_price=new_price,
        new_volatility=new_volatility,
        updated_bid_ask_spread=updated_bid_ask_spread,
        updated_order_book_depth=updated_order_book_depth,
        updated_spread_bid_ask_spread=updated_spread_bid_ask_spread,
        updated_spread_order_book_depth=updated_spread_order_book_depth,
        updated_options_bid_ask_spread=updated_options_bid_ask_spread,
        updated_options_order_book_depth=updated_options_order_book_depth,
        new_gamma_profile=new_gamma_profile,
    )
    return report, dealer_new_inventory
