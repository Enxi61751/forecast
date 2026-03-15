# app/pipeline.py
from __future__ import annotations

from typing import Any

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

    def _safe_float(self, x: Any, default: float = 0.0) -> float:
        try:
            v = float(x)
            if np.isnan(v) or np.isinf(v):
                return default
            return v
        except Exception:
            return default

    def _extract_price_series(self, req) -> np.ndarray:
        """
        从请求中提取按时间排序后的价格序列。
        假定 req.series.price 中每个点都有:
            - t: 时间
            - v: 数值
        """
        price_points = sorted(req.series.price, key=lambda p: p.t)
        y = np.array([self._safe_float(p.v) for p in price_points], dtype=np.float64)

        if y.ndim != 1:
            y = y.reshape(-1)

        # 去掉 nan/inf
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

        # 先走完整接口，拿到更丰富的信息
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
        """
        返回:
            y_final, alpha
        alpha 表示 LGBM 的权重
        """
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

        # 双分支都失败时，退化为“最后一个价格”
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
        # 1) 提取 price 序列
        y = self._extract_price_series(req)
        if y.size == 0:
            raise ValueError("price series is empty after cleaning")
        if y.size < 5:
            raise ValueError("price series is too short; at least 5 points are required")

        # 2) indicators / sentiment
        indicators_last = self._extract_last_indicators(req)
        sentiment_last = self._extract_last_sentiment(req)

        # 3) CEEMDAN
        imfs, ce_full = self._run_ceemdan(y, req)

        # 4) 特征
        # 这里假设 build_tabular_features 能接受 imfs=None
        X_tab, meta = build_tabular_features(
            y=y,
            imfs=imfs,
            indicators_last=indicators_last,
            sentiment_last=sentiment_last,
            events=getattr(req, "events", None),
        )

        # TFT 通常需要更长窗口，这里做兜底
        seq_window = 60
        if y.size < seq_window:
            # 若长度不够，可退化成用现有全部序列
            seq_window = int(y.size)

        X_seq = build_sequence_features(y, window=seq_window)

        # 5) 推理
        y_lgbm = self._predict_lgbm(X_tab)
        y_tft, extreme_prob, out_tft = self._predict_tft(X_seq)

        # 双模型都失败时，最后兜底为最后一个观测值
        if (y_lgbm is None or not np.isfinite(y_lgbm)) and (y_tft is None or not np.isfinite(y_tft)):
            fallback_last = float(y[-1])
            y_final = fallback_last
            alpha = 0.5
        else:
            y_final, alpha = self._fuse_predictions(y_lgbm, y_tft, extreme_prob)

        label, prob = self._risk_label(extreme_prob)

        # 6) explain
        imf_contrib = None
        ce_summary = None
        if imfs is not None and imfs.shape[0] > 0:
            n_imfs = int(imfs.shape[0])
            imf_contrib = [
                {"imf": f"imf{i+1}", "weight": 1.0 / n_imfs}
                for i in range(n_imfs)
            ]

            ce_summary = {
                "enabled": True,
                "n_imfs": n_imfs,
                "length": int(imfs.shape[1]),
                "entropies": (
                    ce_full["entropies"].tolist()
                    if ce_full is not None and ce_full.get("entropies") is not None
                    else None
                ),
                "has_residue": bool(
                    ce_full is not None and ce_full.get("residue") is not None
                ),
            }
        else:
            ce_summary = {
                "enabled": bool(getattr(getattr(req, "ceemdan", None), "enabled", False)),
                "n_imfs": 0,
                "length": int(y.size),
                "entropies": None,
                "has_residue": False,
            }

        feature_order = meta.get("feature_order", []) if isinstance(meta, dict) else []

        explain = {
            "alpha": float(alpha),
            "notes": "pipeline ok; replace stub models with real artifacts when ready",
            "ceemdan": ce_summary,
            "imf_contrib": imf_contrib,
            "lgbm_top_features": [
                {"name": n, "gain": None}
                for n in feature_order[:10]
            ],
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