from __future__ import annotations

from typing import Dict

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .clearing import calibrate_clearing_parameters
from .schemas import (
    ClearingCalibrationObservation,
    ClearingParameters,
    ExecutionState,
    SelfState,
    SimulationInput,
)
from .simulator import run_multi_step, run_single_step


class SingleStepRequest(BaseModel):
    simulation_input: SimulationInput = Field(alias="input")
    current_price: float
    current_volatility: float
    dealer_inventory: int
    max_position_limit: int = 500
    seed: int = 7
    clearing_parameters: ClearingParameters | None = None
    calibration_observations: list[ClearingCalibrationObservation] | None = None
    calibration_file: str | None = None
    agent_states: Dict[str, SelfState] | None = None
    execution_state: ExecutionState | None = None


class MultiStepRequest(BaseModel):
    simulation_input: SimulationInput = Field(alias="input")
    current_price: float
    current_volatility: float
    dealer_inventory: int
    steps: int = 10
    max_position_limit: int = 500
    seed: int = 7
    clearing_parameters: ClearingParameters | None = None
    calibration_observations: list[ClearingCalibrationObservation] | None = None
    calibration_file: str | None = None
    initial_agent_states: Dict[str, SelfState] | None = None
    initial_execution_state: ExecutionState | None = None


class CalibrationRequest(BaseModel):
    observations: list[ClearingCalibrationObservation]


app = FastAPI(title="Stage X2 Agent Service", version="1.0.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/simulate/single")
def simulate_single(request: SingleStepRequest) -> dict:
    result = run_single_step(
        request.simulation_input,
        current_price=request.current_price,
        current_volatility=request.current_volatility,
        dealer_inventory=request.dealer_inventory,
        max_position_limit=request.max_position_limit,
        seed=request.seed,
        clearing_parameters=request.clearing_parameters,
        calibration_observations=request.calibration_observations,
        calibration_file=request.calibration_file,
        agent_states=request.agent_states,
        execution_state=request.execution_state,
    )
    return _dump_result(result)


@app.post("/simulate/multi")
def simulate_multi(request: MultiStepRequest) -> dict:
    result = run_multi_step(
        request.simulation_input,
        current_price=request.current_price,
        current_volatility=request.current_volatility,
        dealer_inventory=request.dealer_inventory,
        steps=request.steps,
        max_position_limit=request.max_position_limit,
        seed=request.seed,
        clearing_parameters=request.clearing_parameters,
        calibration_observations=request.calibration_observations,
        calibration_file=request.calibration_file,
        initial_agent_states=request.initial_agent_states,
        initial_execution_state=request.initial_execution_state,
    )
    return _dump_result(result)


@app.post("/calibrate/clearing")
def calibrate_clearing(request: CalibrationRequest) -> dict:
    parameters = calibrate_clearing_parameters(request.observations)
    return parameters.model_dump()


def _dump_result(result: dict) -> dict:
    dumped: dict = {}
    for key, value in result.items():
        if hasattr(value, "model_dump"):
            dumped[key] = value.model_dump()
        elif isinstance(value, list):
            dumped[key] = [item.model_dump() if hasattr(item, "model_dump") else item for item in value]
        elif isinstance(value, dict):
            dumped[key] = {
                sub_key: sub_value.model_dump() if hasattr(sub_value, "model_dump") else sub_value
                for sub_key, sub_value in value.items()
            }
        else:
            dumped[key] = value
    return dumped


if __name__ == "__main__":
    uvicorn.run("stagex2.api:app", host="0.0.0.0", port=8001)
