# app/pipeline.py
from __future__ import annotations

from typing import Any
from datetime import timezone

import numpy as np

from app.models.ceemdan import CEEMDANDecomposer
from app.models.lgbm_predictor import LGBMPredictor
from app.models.tft_predictor import TFTPredictor
from app.models.ensemble_predictor import EnsemblePredictor
from app.features import build_tabular_features, build_sequence_features
from app.config import settings


class PredictPipeline:
    def __init__(self):
        self.ce = CEEMDANDecomposer()
        self.lgbm = LGBMPredictor()
        self.tft = TFTPredictor()
        # Real models: AlphaModelFrame + TFT CSV + MWUM ensemble
        self.ensemble = EnsemblePredictor()

    def _safe_float(self, x: Any, default: float = 0.0) -> float:
        try:
            v = float(x)
            if np.isnan(v) or np.isinf(v):
                return default
            return v
        except Exception:
            return default

    def _extract_price_series(self, req) -> np.ndarray:
        price_points = sorted(req.series.price, key=lambda p: p.t)
        y = np.array([self._safe_float(p.v) for p in price_points], dtype=np.float64)
        if y.ndim != 1:
            y = y.reshape(-1)
        y = y[np.isfinite(y)]
        return y

    def _extract_last_indicators(self, req) -> dict[str, float]:
        indicators_last: dict[str, float] = {}
        indicators = getattr(req.series, "indicators", {}) or {}
        for name, pts in indicators.items():
            pts_sorted = sorted(pts, key=lambda p: p.t)
            if pts_sorted:
                indicators_last[name] = self._safe_float(pts_sorted[-1].v)
        return indicators_last

    def _extract_last_sentiment(self, req) -> float | None:
        sentiment_points = getattr(req.series, "sentiment_index", None)
        if not sentiment_points:
            return None
        s_sorted = sorted(sentiment_points, key=lambda p: p.t)
        if not s_sorted:
            return None
        return self._safe_float(s_sorted[-1].v)

    def _run_ceemdan(self, y: np.ndarray, req) -> tuple[np.ndarray | None, dict[str, Any] | None]:
        ce_cfg = getattr(req, "ceemdan", None)
        if ce_cfg is None or not getattr(ce_cfg, "enabled", False):
            return None, None

        full = self.ce.decompose_full(
            y,
            trials=getattr(ce_cfg, "trials", 100),
            noise_width=getattr(ce_cfg, "noise_width", 0.2),
            max_imfs=getattr(ce_cfg, "max_imfs", 8),
            seed=getattr(ce_cfg, "seed", 42),
        )
        if full is None:
            return None, None
        imfs = full.get("imfs")
        if imfs is None:
            return None, None
        imfs = np.asarray(imfs, dtype=np.float64)
        if imfs.ndim != 2 or imfs.shape[1] != y.shape[0]:
            return None, None
        return imfs, full

    def _predict_lgbm(self, X_tab: np.ndarray) -> float | None:
        try:
            y_lgbm = self.lgbm.predict(X_tab)
            return self._safe_float(y_lgbm, default=np.nan)
        except Exception:
            return None

    def _predict_tft(self, X_seq: np.ndarray) -> tuple[float | None, float | None, dict[str, Any] | None]:
        try:
            out_tft = self.tft.predict(X_seq)
            y_hat = out_tft.get("y_hat", [np.nan])
            extreme_prob = out_tft.get("extreme_prob", [np.nan])
            y_tft = self._safe_float(y_hat[0] if len(y_hat) > 0 else np.nan, default=np.nan)
            prob = self._safe_float(extreme_prob[0] if len(extreme_prob) > 0 else np.nan, default=np.nan)
            return y_tft, prob, out_tft
        except Exception:
            return None, None, None

    def _fuse_predictions(self, y_lgbm: float | None, y_tft: float | None, extreme_prob: float | None) -> tuple[float, float]:
        has_lgbm = y_lgbm is not None and np.isfinite(y_lgbm)
        has_tft = y_tft is not None and np.isfinite(y_tft)

        if has_lgbm and has_tft:
            prob = 0.5 if (extreme_prob is None or not np.isfinite(extreme_prob)) else float(extreme_prob)
            alpha = 0.7 if prob < 0.6 else 0.4
            y_final = alpha * float(y_lgbm) + (1.0 - alpha) * float(y_tft)
            return float(y_final), float(alpha)
        if has_lgbm:
            return float(y_lgbm), 1.0
        if has_tft:
            return float(y_tft), 0.0
        return np.nan, 0.5

    def _risk_label(self, extreme_prob: float | None) -> tuple[str, float]:
        if extreme_prob is None or not np.isfinite(extreme_prob):
            return "UNKNOWN", 0.0
        p = float(extreme_prob)
        if p >= 0.7:
            return "HIGH_RISK", p
        if p >= 0.4:
            return "MID_RISK", p
        return "LOW_RISK", p

    def run(self, req):
        # 1) Extract price series from request
        y = self._extract_price_series(req)
        if y.size == 0:
            raise ValueError("price series is empty after cleaning")
        if y.size < 5:
            raise ValueError("price series is too short; at least 5 points are required")

        last_price = float(y[-1])

        # 2) Determine query date
        query_date = None
        if req.asOf is not None:
            try:
                query_date = req.asOf.date() if hasattr(req.asOf, "date") else req.asOf
            except Exception:
                query_date = None

        # 3) Try real ensemble (AlphaModelFrame + TFT CSV + MWUM weights)
        if not settings.USE_STUB:
            try:
                point, lower_90, upper_90, ens_explain = self.ensemble.predict(
                    query_date=query_date, last_price=last_price
                )
                if np.isfinite(point):
                    # Derive risk from relative deviation
                    deviation = abs(point - last_price) / (last_price + 1e-9)
                    if deviation >= 0.05:
                        risk_label, risk_prob = "HIGH_RISK", min(deviation * 10, 1.0)
                    elif deviation >= 0.02:
                        risk_label, risk_prob = "MID_RISK", deviation * 20
                    else:
                        risk_label, risk_prob = "LOW_RISK", deviation * 10

                    explain = {
                        "alpha": ens_explain.get("weight_alpha", 0.5),
                        "notes": "real models: AlphaModelFrame DoubleEnsemble + TFT CSV + MWUM",
                        "ceemdan": {"enabled": False, "n_imfs": 0, "length": int(y.size),
                                    "entropies": None, "has_residue": False},
                        "imf_contrib": None,
                        "lgbm_top_features": [],
                        "model_outputs": {
                            "alpha": ens_explain.get("alpha_price"),
                            "tft": ens_explain.get("tft_price"),
                            "ensemble": point,
                            "lower_90": lower_90,
                            "upper_90": upper_90,
                        },
                    }
                    extra = {"alpha": ens_explain.get("alpha_price"), "tft": ens_explain.get("tft_price")}
                    return float(point), {"label": risk_label, "prob": float(risk_prob)}, explain, extra
            except Exception:
                pass  # fall through to stub pipeline

        # 4) Fallback: stub/legacy pipeline (CEEMDAN + old lgbm + old tft stubs)
        indicators_last = self._extract_last_indicators(req)
        sentiment_last = self._extract_last_sentiment(req)
        imfs, ce_full = self._run_ceemdan(y, req)

        X_tab, meta = build_tabular_features(
            y=y,
            imfs=imfs,
            indicators_last=indicators_last,
            sentiment_last=sentiment_last,
            events=getattr(req, "events", None),
        )

        seq_window = min(60, int(y.size))
        X_seq = build_sequence_features(y, window=seq_window)

        y_lgbm = self._predict_lgbm(X_tab)
        y_tft, extreme_prob, out_tft = self._predict_tft(X_seq)

        if (y_lgbm is None or not np.isfinite(y_lgbm)) and (y_tft is None or not np.isfinite(y_tft)):
            y_final = last_price
            alpha = 0.5
        else:
            y_final, alpha = self._fuse_predictions(y_lgbm, y_tft, extreme_prob)

        label, prob = self._risk_label(extreme_prob)

        imf_contrib = None
        ce_summary = None
        if imfs is not None and imfs.shape[0] > 0:
            n_imfs = int(imfs.shape[0])
            imf_contrib = [{"imf": f"imf{i+1}", "weight": 1.0 / n_imfs} for i in range(n_imfs)]
            ce_summary = {
                "enabled": True, "n_imfs": n_imfs, "length": int(imfs.shape[1]),
                "entropies": (ce_full["entropies"].tolist()
                              if ce_full is not None and ce_full.get("entropies") is not None else None),
                "has_residue": bool(ce_full is not None and ce_full.get("residue") is not None),
            }
        else:
            ce_summary = {
                "enabled": bool(getattr(getattr(req, "ceemdan", None), "enabled", False)),
                "n_imfs": 0, "length": int(y.size), "entropies": None, "has_residue": False,
            }

        feature_order = meta.get("feature_order", []) if isinstance(meta, dict) else []
        explain = {
            "alpha": float(alpha),
            "notes": "stub pipeline active",
            "ceemdan": ce_summary,
            "imf_contrib": imf_contrib,
            "lgbm_top_features": [{"name": n, "gain": None} for n in feature_order[:10]],
            "model_outputs": {
                "lgbm": None if y_lgbm is None else float(y_lgbm),
                "tft": None if y_tft is None else float(y_tft),
            },
        }
        extra = {
            "lgbm": None if y_lgbm is None else float(y_lgbm),
            "tft": None if y_tft is None else float(y_tft),
        }
        return float(y_final), {"label": label, "prob": float(prob)}, explain, extra
