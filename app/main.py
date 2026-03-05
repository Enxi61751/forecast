# app/main.py
from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse, Forecast, ExtremeClass, Explain, TimePoint
from app.pipeline import PredictPipeline
from datetime import datetime, timezone, timedelta

app = FastAPI(title="CitiCup Model Service", version="0.1.0")
pipe = PredictPipeline()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    y_final, extreme, explain, raw = pipe.run(req)

    # 这里示例：预测 T+1；你们可以按 horizon 输出多步
    t_next = (req.asOf or datetime.now(timezone.utc)) + timedelta(days=1)

    forecast = Forecast(
        point=[TimePoint(t=t_next, v=float(y_final))],
        lower=None,
        upper=None,
        raw=raw
    )

    return PredictResponse(
        forecast=forecast,
        extremeClass=ExtremeClass(label=extreme["label"], prob=float(extreme["prob"])),
        explain=Explain(**explain)
    )