from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stagex2.schemas import AgentActionOutput  # noqa: E402


def main() -> None:
    example_output = AgentActionOutput.model_validate(
        {
            "direction": 1,
            "size_score": 1,
            "instrument_pref": "spread",
            "aggressiveness": 0.4,
            "horizon": "3d",
            "rationale": "Calendar spread is 3 standard deviations above normal, so the trader fades the move.",
            "confidence": 0.72,
            "is_risk_triggered": False,
            "memory_to_save": "Faded the stretched calendar spread and will reassess after liquidity normalizes.",
        }
    )
    print(json.dumps(example_output.model_dump(), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
