from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stagex2.decision import build_prompt_messages  # noqa: E402
from stagex2.perception import derive_risk_tags  # noqa: E402
from stagex2.schemas import SimulationInput  # noqa: E402


def build_sample_input() -> SimulationInput:
    return SimulationInput.model_validate(
        {
            "environment": {
                "factor_snapshot": {
                    "current_price": 78.2,
                    "trend_score": 1.8,
                    "rsi_status": "Overbought",
                    "term_structure": "Backwardation",
                    "current_calendar_spread": 2.4,
                    "historical_spread_mean": 0.9,
                    "historical_spread_std": 0.5,
                },
                "tail_risk_report": {
                    "gamma_profile": "Short Gamma",
                    "liquidity_stress": 0.82,
                },
                "market_microstructure": {
                    "bid_ask_spread": 0.18,
                    "order_book_depth": "Thin",
                    "spread_bid_ask_spread": 0.09,
                    "spread_order_book_depth": "Normal",
                    "options_bid_ask_spread": 0.31,
                    "options_order_book_depth": "Thin",
                },
                "session_info": {
                    "phase": "Close",
                    "time_to_close": 10,
                },
            },
            "event": {
                "headline": "Port strike extends and crude inventory falls sharply",
                "body": "Logistics disruption and inventory shortage raise near-term supply concerns.",
                "source": "Central Bank Statement",
                "impact_type": "Supply Shock",
            },
            "self": {
                "role": "Spread Trader",
                "mandate": "Relative value",
                "hedger_type": "neutral",
                "max_leverage": 3.0,
                "stop_loss_pct": 0.05,
                "position": 0,
                "unrealized_pnl": 0,
                "unrealized_pnl_pct": 0.0,
                "cash_level": 100000,
                "last_action": "Hold",
                "consecutive_losses": 0,
                "view_history": "Curve looked stretched but not yet actionable.",
            },
        }
    )


def main() -> None:
    simulation_input = build_sample_input()
    risk_tags = derive_risk_tags(
        simulation_input.environment,
        simulation_input.self_state,
        assumed_horizon="3d",
    )
    prompt_messages = build_prompt_messages(
        event=simulation_input.event,
        environment=simulation_input.environment,
        self_state=simulation_input.self_state,
        risk_tags=risk_tags,
    )
    print(json.dumps([message for message in prompt_messages], ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
