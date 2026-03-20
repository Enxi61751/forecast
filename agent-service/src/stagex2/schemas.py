from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RsiStatus = Literal["Overbought", "Neutral", "Oversold"]
TermStructure = Literal["Contango", "Backwardation"]
GammaProfile = Literal["Long Gamma", "Neutral", "Short Gamma"]
BookDepth = Literal["Deep", "Normal", "Thin"]
SessionPhase = Literal["Open", "Mid-Day", "Close", "Overnight"]
ActionDirection = Literal[1, 0, -1]
OrderSide = Literal["BUY", "SELL", "NONE"]
OrderType = Literal["MARKET", "LIMIT"]
InstrumentPref = Literal["front", "spread", "options", "back"]
Horizon = Literal["Intraday", "1d", "1w", "3d", "1m", "intraday"]
TrendDirection = Literal["Up", "Down", "Flat"]
MomentumStrength = Literal["Strong", "Moderate", "Weak"]
HeadlineBias = Literal["Bullish", "Bearish", "Neutral"]
HedgerType = Literal["consumer", "producer", "neutral"]
BookName = Literal["front", "spread", "options"]
OrderStatus = Literal["WORKING", "PARTIAL", "FILLED", "CANCELLED", "EXPIRED"]


class FactorSnapshot(BaseModel):
    current_price: float | None = None
    trend_score: float
    rsi_status: RsiStatus
    term_structure: TermStructure
    current_calendar_spread: float | None = None
    historical_spread_mean: float | None = None
    historical_spread_std: float | None = Field(default=None, gt=0.0)


class TailRiskReport(BaseModel):
    gamma_profile: GammaProfile
    liquidity_stress: float = Field(ge=0.0, le=1.0)


class MarketMicrostructure(BaseModel):
    bid_ask_spread: float = Field(gt=0.0)
    order_book_depth: BookDepth
    spread_bid_ask_spread: float | None = Field(default=None, gt=0.0)
    spread_order_book_depth: BookDepth | None = None
    options_bid_ask_spread: float | None = Field(default=None, gt=0.0)
    options_order_book_depth: BookDepth | None = None


class SessionInfo(BaseModel):
    phase: SessionPhase
    time_to_close: int = Field(ge=0)


class Environment(BaseModel):
    factor_snapshot: FactorSnapshot
    tail_risk_report: TailRiskReport
    market_microstructure: MarketMicrostructure
    session_info: SessionInfo


class Event(BaseModel):
    headline: str
    body: str
    source: str
    impact_type: str
    sentiment_score: float | None = Field(default=None, ge=-3.0, le=3.0)


class SelfState(BaseModel):
    role: str
    mandate: str
    hedger_type: HedgerType = "neutral"
    max_leverage: float
    stop_loss_pct: float
    position: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    cash_level: float
    last_action: str
    consecutive_losses: int = Field(ge=0)
    view_history: str


class SimulationInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    environment: Environment
    event: Event
    self_state: SelfState = Field(alias="self")


class PerceptionContext(BaseModel):
    risk_tags: List[str]
    trend_direction: TrendDirection
    momentum_strength: MomentumStrength
    spread_zscore: float | None = None
    term_structure_signal: str
    execution_cost_state: str
    source_reliability: str
    headline_sentiment_score: float
    headline_bias: HeadlineBias
    time_pressure: str
    pnl_state: str
    capital_state: str
    discipline_state: str
    leverage_headroom_contracts: int = Field(ge=0)


class AgentActionOutput(BaseModel):
    direction: ActionDirection
    size_score: int = Field(ge=-3, le=3)
    instrument_pref: InstrumentPref
    aggressiveness: float = Field(ge=0.0, le=1.0)
    horizon: Horizon
    rationale: str = Field(max_length=600)
    confidence: float = Field(ge=0.0, le=1.0)
    is_risk_triggered: bool
    memory_to_save: str = Field(max_length=300)

    @model_validator(mode="after")
    def validate_direction_size_consistency(self) -> "AgentActionOutput":
        if self.direction == 0 and self.size_score != 0:
            raise ValueError("If direction is 0, size_score must be 0.")
        if self.direction == 1 and self.size_score < 0:
            raise ValueError("If direction is 1, size_score must be >= 0.")
        if self.direction == -1 and self.size_score > 0:
            raise ValueError("If direction is -1, size_score must be <= 0.")
        return self


class StandardOrder(BaseModel):
    order_id: str
    parent_order_id: str | None = None
    agent_id: str
    book: BookName
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int = Field(ge=0)
    filled_quantity: int = Field(default=0, ge=0)
    remaining_quantity: int = Field(default=0, ge=0)
    ttl_steps: int = Field(default=0, ge=0)
    horizon: Horizon
    status: OrderStatus = "WORKING"
    aggressiveness: float = Field(ge=0.0, le=1.0)
    price_strategy: str
    reason: str = Field(max_length=600)


class ClearingInput(BaseModel):
    order_flow: List[StandardOrder]
    current_price: float = Field(gt=0)
    current_liquidity_stress: float = Field(ge=0.0, le=1.0)
    current_bid_ask_spread: float = Field(gt=0.0)
    current_spread_bid_ask_spread: float | None = Field(default=None, gt=0.0)
    current_options_bid_ask_spread: float | None = Field(default=None, gt=0.0)
    current_volatility: float = Field(ge=0.0)
    dealer_inventory: int


class ClearingParameters(BaseModel):
    lambda_base: float = Field(gt=0.0)
    alpha_recovery: float = Field(ge=0.0)
    beta_consumption: float = Field(ge=0.0)
    noise_scale: float = Field(ge=0.0)
    volatility_sensitivity: float = Field(ge=0.0)
    short_gamma_inventory_threshold: int = Field(lt=0)
    long_gamma_inventory_threshold: int = Field(gt=0)
    short_gamma_vol_multiplier: float = Field(ge=1.0)
    spread_widening_multiplier: float = Field(ge=0.0)
    temporary_impact_multiplier: float = Field(ge=0.0)


class ClearingCalibrationObservation(BaseModel):
    effective_net_flow: float
    liquidity_stress: float = Field(ge=0.0, le=1.0)
    current_bid_ask_spread: float = Field(gt=0.0)
    urgency_pressure: float = Field(ge=0.0)
    current_price: float = Field(gt=0.0)
    price_change: float
    total_volume: float = Field(ge=0.0)
    next_liquidity_stress: float = Field(ge=0.0, le=1.0)
    current_volatility: float = Field(ge=0.0)
    next_volatility: float = Field(ge=0.0)
    next_gamma_profile: GammaProfile
    updated_bid_ask_spread: float = Field(gt=0.0)


class MarketSimReport(BaseModel):
    simulated_flow_pressure: float
    liquidity_stress: float = Field(ge=0.0, le=1.0)
    gamma_squeeze_risk: float = Field(ge=0.0, le=1.0)
    spread_pressure: float
    new_price: float = Field(gt=0)
    new_volatility: float = Field(ge=0.0)
    updated_bid_ask_spread: float = Field(gt=0.0)
    updated_order_book_depth: BookDepth
    updated_spread_bid_ask_spread: float = Field(gt=0.0)
    updated_spread_order_book_depth: BookDepth
    updated_options_bid_ask_spread: float = Field(gt=0.0)
    updated_options_order_book_depth: BookDepth
    new_gamma_profile: GammaProfile


class ExecutionState(BaseModel):
    working_orders: List[StandardOrder] = Field(default_factory=list)
    next_order_sequence: int = 1


class ExecutionReport(BaseModel):
    submitted_orders: List[StandardOrder] = Field(default_factory=list)
    executed_orders: List[StandardOrder] = Field(default_factory=list)
    cancelled_orders: List[StandardOrder] = Field(default_factory=list)
    expired_orders: List[StandardOrder] = Field(default_factory=list)
    working_orders: List[StandardOrder] = Field(default_factory=list)
