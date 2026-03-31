<<<<<<< HEAD
# app/pipeline.py
=======
>>>>>>> c3c3a7b (save local files)
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
<<<<<<< HEAD
        # Real models: AlphaModelFrame + TFT CSV + MWUM ensemble
=======
>>>>>>> c3c3a7b (save local files)
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
<<<<<<< HEAD
        imfs = full.get("imfs")
        if imfs is None:
            return None, None
        imfs = np.asarray(imfs, dtype=np.float64)
        if imfs.ndim != 2 or imfs.shape[1] != y.shape[0]:
            return None, None
=======

        imfs = full.get("imfs")
        if imfs is None:
            return None, None

        imfs = np.asarray(imfs, dtype=np.float64)
        if imfs.ndim != 2 or imfs.shape[1] != y.shape[0]:
            return None, None

>>>>>>> c3c3a7b (save local files)
        return imfs, full

    def _predict_lgbm(self, X_tab: np.ndarray) -> float | None:
        try:
            y_lgbm = self.lgbm.predict(X_tab)
            return self._safe_float(y_lgbm, default=np.nan)
        except Exception:
            return None

    def _predict_tft(self, X_seq: np.ndarray) -> tuple[float | None, float | None, dict[str, Any] | None]:
        try:
<<<<<<< HEAD
            out_tft = self.tft.predict(X_seq)
            y_hat = out_tft.get("y_hat", [np.nan])
            extreme_prob = out_tft.get("extreme_prob", [np.nan])
            y_tft = self._safe_float(y_hat[0] if len(y_hat) > 0 else np.nan, default=np.nan)
            prob = self._safe_float(extreme_prob[0] if len(extreme_prob) > 0 else np.nan, default=np.nan)
=======
            out_tft = self.tft.predict(X_seq) or {}
            y_hat = out_tft.get("y_hat", [np.nan])
            extreme_prob = out_tft.get("extreme_prob", [np.nan])

            y_tft = self._safe_float(y_hat[0] if len(y_hat) > 0 else np.nan, default=np.nan)
            prob = self._safe_float(
                extreme_prob[0] if len(extreme_prob) > 0 else np.nan,
                default=np.nan,
            )
>>>>>>> c3c3a7b (save local files)
            return y_tft, prob, out_tft
        except Exception:
            return None, None, None

<<<<<<< HEAD
    def _fuse_predictions(self, y_lgbm: float | None, y_tft: float | None, extreme_prob: float | None) -> tuple[float, float]:
=======
    def _fuse_predictions(
        self,
        y_lgbm: float | None,
        y_tft: float | None,
        extreme_prob: float | None
    ) -> tuple[float, float]:
>>>>>>> c3c3a7b (save local files)
        has_lgbm = y_lgbm is not None and np.isfinite(y_lgbm)
        has_tft = y_tft is not None and np.isfinite(y_tft)

        if has_lgbm and has_tft:
            prob = 0.5 if (extreme_prob is None or not np.isfinite(extreme_prob)) else float(extreme_prob)
            alpha = 0.7 if prob < 0.6 else 0.4
            y_final = alpha * float(y_lgbm) + (1.0 - alpha) * float(y_tft)
            return float(y_final), float(alpha)
<<<<<<< HEAD
        if has_lgbm:
            return float(y_lgbm), 1.0
        if has_tft:
            return float(y_tft), 0.0
=======

        if has_lgbm:
            return float(y_lgbm), 1.0

        if has_tft:
            return float(y_tft), 0.0

>>>>>>> c3c3a7b (save local files)
        return np.nan, 0.5

    def _risk_label(self, extreme_prob: float | None) -> tuple[str, float]:
        if extreme_prob is None or not np.isfinite(extreme_prob):
            return "UNKNOWN", 0.0
<<<<<<< HEAD
=======

>>>>>>> c3c3a7b (save local files)
        p = float(extreme_prob)
        if p >= 0.7:
            return "HIGH_RISK", p
        if p >= 0.4:
            return "MID_RISK", p
        return "LOW_RISK", p

<<<<<<< HEAD
    def run(self, req):
        # 1) Extract price series (series is optional; Spring Boot may send flat payload without it)
=======
    def _safe_feature_importance_item(self, item: Any) -> dict[str, Any] | None:
        if not isinstance(item, dict):
            return None

        feature = str(item.get("feature", "")).strip()
        group = str(item.get("group", "")).strip()
        avg_weight = self._safe_float(item.get("avg_weight", np.nan), default=np.nan)

        if not feature or not np.isfinite(avg_weight):
            return None

        return {
            "feature": feature,
            "group": group or "unknown",
            "avg_weight": float(avg_weight),
        }

    def _normalize_feature_importance(self, out_tft: dict[str, Any] | None) -> list[dict[str, Any]]:
        if not isinstance(out_tft, dict):
            return []

        candidates = [
            out_tft.get("feature_importance"),
            out_tft.get("variable_importance"),
            out_tft.get("importance"),
        ]

        for candidate in candidates:
            if isinstance(candidate, list):
                rows = []
                for item in candidate:
                    parsed = self._safe_feature_importance_item(item)
                    if parsed is not None:
                        rows.append(parsed)
                if rows:
                    rows.sort(key=lambda x: x["avg_weight"], reverse=True)
                    return rows

        hist = out_tft.get("hist_feature_importance")
        known = out_tft.get("known_future_feature_importance")

        rows = []
        if isinstance(hist, list):
            for item in hist:
                parsed = self._safe_feature_importance_item(item)
                if parsed is not None:
                    rows.append(parsed)

        if isinstance(known, list):
            for item in known:
                parsed = self._safe_feature_importance_item(item)
                if parsed is not None:
                    rows.append(parsed)

        rows.sort(key=lambda x: x["avg_weight"], reverse=True)
        return rows

    def _split_feature_importance(
        self,
        rows: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        hist_rows = []
        known_rows = []

        for row in rows:
            group = str(row.get("group", "")).lower()
            if group == "hist":
                hist_rows.append(row)
            elif group == "known_future":
                known_rows.append(row)

        hist_rows.sort(key=lambda x: x["avg_weight"], reverse=True)
        known_rows.sort(key=lambda x: x["avg_weight"], reverse=True)
        return hist_rows, known_rows

    def _build_tft_charts(self, rows: list[dict[str, Any]], top_n: int = 10) -> dict[str, list[dict[str, Any]]]:
        top_rows = rows[:top_n]
        hist_rows, known_rows = self._split_feature_importance(rows)

        return {
            "feature_importance_bar": [
                {
                    "name": r["feature"],
                    "value": float(r["avg_weight"]),
                    "group": r["group"],
                }
                for r in top_rows
            ],
            "hist_feature_importance_bar": [
                {
                    "name": r["feature"],
                    "value": float(r["avg_weight"]),
                    "group": r["group"],
                }
                for r in hist_rows[:top_n]
            ],
            "known_future_feature_importance_bar": [
                {
                    "name": r["feature"],
                    "value": float(r["avg_weight"]),
                    "group": r["group"],
                }
                for r in known_rows[:top_n]
            ],
        }

    def _extract_tft_explain(self, out_tft: dict[str, Any] | None, y_tft: float | None) -> dict[str, Any] | None:
        if not isinstance(out_tft, dict):
            return None

        feature_rows = self._normalize_feature_importance(out_tft)
        hist_rows, known_rows = self._split_feature_importance(feature_rows)

        quantiles = out_tft.get("quantiles")
        if not isinstance(quantiles, list):
            quantiles = None

        charts = self._build_tft_charts(feature_rows, top_n=10) if feature_rows else None

        has_payload = any([
            quantiles is not None,
            y_tft is not None and np.isfinite(y_tft),
            bool(feature_rows),
            bool(out_tft),
        ])

        if not has_payload:
            return None

        return {
            "quantiles": quantiles,
            "median_prediction": None if y_tft is None or not np.isfinite(y_tft) else float(y_tft),
            "feature_importance": feature_rows if feature_rows else None,
            "hist_feature_importance": hist_rows if hist_rows else None,
            "known_future_feature_importance": known_rows if known_rows else None,
            "charts": charts,
            "raw": out_tft,
        }

    def run(self, req):
        # 1) Extract price series
>>>>>>> c3c3a7b (save local files)
        if req.series is not None and req.series.price:
            y = self._extract_price_series(req)
            y = y[np.isfinite(y)]
        else:
            y = np.array([], dtype=np.float64)

<<<<<<< HEAD
        # Use last known price if series provided, otherwise default to 80 USD (model will override)
=======
>>>>>>> c3c3a7b (save local files)
        last_price = float(y[-1]) if y.size > 0 else 80.0

        # 2) Determine query date
        query_date = None
        if req.asOf is not None:
            try:
                query_date = req.asOf.date() if hasattr(req.asOf, "date") else req.asOf
            except Exception:
                query_date = None

<<<<<<< HEAD
        # 3) Try real ensemble (AlphaModelFrame + TFT CSV + MWUM weights)
        if not settings.USE_STUB:
            try:
                point, lower_90, upper_90, ens_explain = self.ensemble.predict(
                    query_date=query_date, last_price=last_price
                )
                if np.isfinite(point):
                    # Derive risk from relative deviation
=======
        # 3) Try real ensemble
        if not settings.USE_STUB:
            try:
                point, lower_90, upper_90, ens_explain = self.ensemble.predict(
                    query_date=query_date,
                    last_price=last_price,
                )
                if np.isfinite(point):
>>>>>>> c3c3a7b (save local files)
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
<<<<<<< HEAD
                        "ceemdan": {"enabled": False, "n_imfs": 0, "length": int(y.size),
                                    "entropies": None, "has_residue": False},
=======
                        "ceemdan": {
                            "enabled": False,
                            "n_imfs": 0,
                            "length": int(y.size),
                            "entropies": None,
                            "has_residue": False,
                        },
>>>>>>> c3c3a7b (save local files)
                        "imf_contrib": None,
                        "lgbm_top_features": [],
                        "model_outputs": {
                            "alpha": ens_explain.get("alpha_price"),
                            "tft": ens_explain.get("tft_price"),
                            "ensemble": point,
                            "lower_90": lower_90,
                            "upper_90": upper_90,
                        },
<<<<<<< HEAD
                    }
                    extra = {"alpha": ens_explain.get("alpha_price"), "tft": ens_explain.get("tft_price")}
                    return float(point), {"label": risk_label, "prob": float(risk_prob)}, explain, extra
            except Exception:
                pass  # fall through to stub pipeline

        # 4) Fallback: stub/legacy pipeline (CEEMDAN + old lgbm + old tft stubs)
        # Requires at least 5 price points; if no series provided skip CEEMDAN/feature building
        if y.size < 5:
            return float(last_price), {"label": "UNKNOWN", "prob": 0.0}, {
                "alpha": 0.5, "notes": "no series provided; stub fallback",
                "ceemdan": {"enabled": False, "n_imfs": 0, "length": 0,
                            "entropies": None, "has_residue": False},
                "imf_contrib": None, "lgbm_top_features": [],
                "model_outputs": {"lgbm": None, "tft": None},
            }, {"lgbm": None, "tft": None}
=======
                        "tft": {
                            "quantiles": None,
                            "median_prediction": self._safe_float(
                                ens_explain.get("tft_price", np.nan),
                                default=np.nan,
                            ) if ens_explain.get("tft_price") is not None else None,
                            "feature_importance": None,
                            "hist_feature_importance": None,
                            "known_future_feature_importance": None,
                            "charts": None,
                            "raw": {
                                "source": "ensemble_predictor",
                                "tft_price": ens_explain.get("tft_price"),
                            },
                        },
                    }
                    extra = {
                        "alpha": ens_explain.get("alpha_price"),
                        "tft": ens_explain.get("tft_price"),
                    }
                    return float(point), {"label": risk_label, "prob": float(risk_prob)}, explain, extra
            except Exception:
                pass

        # 4) Fallback: old/stub pipeline
        if y.size < 5:
            return float(last_price), {"label": "UNKNOWN", "prob": 0.0}, {
                "alpha": 0.5,
                "notes": "no series provided; stub fallback",
                "ceemdan": {
                    "enabled": False,
                    "n_imfs": 0,
                    "length": 0,
                    "entropies": None,
                    "has_residue": False,
                },
                "imf_contrib": None,
                "lgbm_top_features": [],
                "model_outputs": {
                    "lgbm": None,
                    "tft": None,
                },
                "tft": None,
            }, {
                "lgbm": None,
                "tft": None,
            }
>>>>>>> c3c3a7b (save local files)

        indicators_last = self._extract_last_indicators(req) if req.series else {}
        sentiment_last = self._extract_last_sentiment(req) if req.series else None
        imfs, ce_full = self._run_ceemdan(y, req)

        X_tab, meta = build_tabular_features(
            y=y,
            imfs=imfs,
            indicators_last=indicators_last,
            sentiment_last=sentiment_last,
            events=getattr(req, "events", None) or [],
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
<<<<<<< HEAD
                "enabled": True, "n_imfs": n_imfs, "length": int(imfs.shape[1]),
                "entropies": (ce_full["entropies"].tolist()
                              if ce_full is not None and ce_full.get("entropies") is not None else None),
=======
                "enabled": True,
                "n_imfs": n_imfs,
                "length": int(imfs.shape[1]),
                "entropies": (
                    ce_full["entropies"].tolist()
                    if ce_full is not None and ce_full.get("entropies") is not None
                    else None
                ),
>>>>>>> c3c3a7b (save local files)
                "has_residue": bool(ce_full is not None and ce_full.get("residue") is not None),
            }
        else:
            ce_summary = {
                "enabled": bool(getattr(getattr(req, "ceemdan", None), "enabled", False)),
<<<<<<< HEAD
                "n_imfs": 0, "length": int(y.size), "entropies": None, "has_residue": False,
            }

        feature_order = meta.get("feature_order", []) if isinstance(meta, dict) else []
=======
                "n_imfs": 0,
                "length": int(y.size),
                "entropies": None,
                "has_residue": False,
            }

        feature_order = meta.get("feature_order", []) if isinstance(meta, dict) else []
        tft_explain = self._extract_tft_explain(out_tft, y_tft)

>>>>>>> c3c3a7b (save local files)
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
<<<<<<< HEAD
        }
=======
            "tft": tft_explain,
        }

>>>>>>> c3c3a7b (save local files)
        extra = {
            "lgbm": None if y_lgbm is None else float(y_lgbm),
            "tft": None if y_tft is None else float(y_tft),
        }
<<<<<<< HEAD
        return float(y_final), {"label": label, "prob": float(prob)}, explain, extra
=======

        return float(y_final), {"label": label, "prob": float(prob)}, explain, extra
>>>>>>> c3c3a7b (save local files)
