from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException

from app.pipeline import PredictPipeline
from app.schemas import (
    PredictRequest,
    PredictResponse,
    Forecast,
    ExtremeClass,
    Explain,
    TimePoint,
)

app = FastAPI(title="CitiCup Model Service", version="0.1.0")
pipe = PredictPipeline()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        y_final, extreme, explain, raw = pipe.run(req)

        # 当前先按 T+1 输出；后续可根据 req.horizon 扩展为多步预测
        base_time = req.asOf or datetime.now(timezone.utc)
        t_next = base_time + timedelta(days=1)

        forecast = Forecast(
            point=[TimePoint(t=t_next, v=float(y_final))],
            lower=None,
            upper=None,
            raw=raw,
        )

        return PredictResponse(
            forecast=forecast,
            extremeClass=ExtremeClass(
                label=str(extreme["label"]),
                prob=float(extreme["prob"]),
            ),
            explain=Explain(**explain),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"predict failed: {str(e)}")