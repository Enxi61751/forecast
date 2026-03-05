# app/pipeline.py
import numpy as np
from app.models.ceemdan import CEEMDANDecomposer
from app.models.lgbm_predictor import LGBMPredictor
from app.models.tft_predictor import TFTPredictor
from app.features import build_tabular_features, build_sequence_features

class PredictPipeline:
    def __init__(self):
        self.ce = CEEMDANDecomposer()
        self.lgbm = LGBMPredictor()
        self.tft = TFTPredictor()

    def run(self, req):
        # 1) 提取 price 序列
        price = sorted(req.series.price, key=lambda p: p.t)
        y = np.array([p.v for p in price], dtype=float)

        # 2) indicators last
        indicators_last = {}
        for name, pts in req.series.indicators.items():
            pts_sorted = sorted(pts, key=lambda p: p.t)
            if pts_sorted:
                indicators_last[name] = float(pts_sorted[-1].v)

        sentiment_last = None
        if req.series.sentiment_index:
            s_sorted = sorted(req.series.sentiment_index, key=lambda p: p.t)
            sentiment_last = float(s_sorted[-1].v) if s_sorted else None

        # 3) CEEMDAN
        imfs = None
        if req.ceemdan.enabled:
            imfs = self.ce.decompose(
                y,
                trials=req.ceemdan.trials,
                noise_width=req.ceemdan.noise_width,
                max_imfs=req.ceemdan.max_imfs,
            )

        # 4) 特征
        X_tab, meta = build_tabular_features(y, imfs, indicators_last, sentiment_last, req.events)
        X_seq = build_sequence_features(y, window=60)

        # 5) 推理
        y_lgbm = self.lgbm.predict(X_tab)
        out_tft = self.tft.predict(X_seq)
        y_tft = float(out_tft["y_hat"][0])
        extreme_prob = float(out_tft["extreme_prob"][0])

        # 6) 融合（gating：极端高 -> 更依赖 TFT）
        alpha = 0.7 if extreme_prob < 0.6 else 0.4
        y_final = alpha * y_lgbm + (1 - alpha) * y_tft

        label = "HIGH_RISK" if extreme_prob >= 0.7 else ("MID_RISK" if extreme_prob >= 0.4 else "LOW_RISK")

        # 7) explain（先给最小信息，后续加 SHAP/attention）
        explain = {
            "alpha": alpha,
            "notes": "pipeline ok; replace stub models with real artifacts when ready",
            "imf_contrib": [{"imf": f"imf{i}", "weight": 1.0/imfs.shape[0]} for i in range(imfs.shape[0])] if imfs is not None else None,
            "lgbm_top_features": [{"name": n, "gain": None} for n in meta["feature_order"][:10]],
        }

        return y_final, {"label": label, "prob": extreme_prob}, explain, {"lgbm": y_lgbm, "tft": y_tft}