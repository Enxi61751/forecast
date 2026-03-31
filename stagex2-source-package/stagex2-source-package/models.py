from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stagex2.schemas import AgentActionOutput, ClearingCalibrationObservation, SimulationInput  # noqa: E402


def main() -> None:
    payload = {
        "simulation_input_schema": SimulationInput.model_json_schema(),
        "agent_output_schema": AgentActionOutput.model_json_schema(),
        "clearing_calibration_observation_schema": ClearingCalibrationObservation.model_json_schema(),
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
