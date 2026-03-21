# app/models/alpha_predictor.py
"""
Wraps the AlphaModelFrame DoubleEnsemble pkl models for inference.

The AlphaModelFrame saves model checkpoints as:
    model_train/model_de_{YYYYMMDD}.pkl
Each pkl contains:
    {
        'model_list': [lgb.LGBMRegressor, ...],          # 4 sub-models
        'selected_features_list': [[int, ...], ...],     # feature indices per sub-model
    }

For inference we load the latest checkpoint whose date <= query date,
then average predictions from all sub-models using their respective
feature subsets.

If the data CSV is available, we look up the features directly.
Otherwise (no CSV) we fall back to the pre-computed predictions.pkl.
"""
from __future__ import annotations

import os
import pickle
import logging
from datetime import date, datetime
from typing import Optional

import numpy as np

from app.config import settings

log = logging.getLogger(__name__)


class AlphaPredictor:
    """Loads the pre-trained DoubleEnsemble pkl and runs inference."""

    def __init__(self):
        self._available = False
        self._predictions: dict[int, float] = {}   # pre-computed returns: {YYYYMMDD: ret}
        self._data = None                           # pandas DataFrame of feature CSV
        self._model_cache: dict[int, dict] = {}    # cache of loaded pkl files

        if settings.USE_STUB:
            return

        self._load_predictions()
        self._load_data_csv()
        self._available = True

    # ── loading helpers ─────────────────────────────────────────────────────

    def _load_predictions(self):
        path = settings.ALPHA_PREDICTIONS_PKL
        if not os.path.isfile(path):
            log.warning("AlphaPredictor: predictions.pkl not found at %s", path)
            return
        try:
            with open(path, "rb") as f:
                raw = pickle.load(f)
            self._predictions = {int(k): float(v) for k, v in raw.items() if v is not None}
            log.info("AlphaPredictor: loaded %d pre-computed return predictions", len(self._predictions))
        except Exception as e:
            log.warning("AlphaPredictor: failed to load predictions.pkl: %s", e)

    def _load_data_csv(self):
        path = settings.ALPHA_DATA_CSV
        if not os.path.isfile(path):
            log.warning("AlphaPredictor: data CSV not found at %s", path)
            return
        try:
            import pandas as pd
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            # Convert Timestamp index to YYYYMMDD int for fast lookup
            df.index = df.index.map(lambda x: int(str(x)[:10].replace("-", "")))
            self._data = df
            log.info("AlphaPredictor: loaded data CSV with shape %s", df.shape)
        except Exception as e:
            log.warning("AlphaPredictor: failed to load data CSV: %s", e)

    def _load_model_for_date(self, query_date_int: int) -> Optional[dict]:
        """Load the latest checkpoint whose date <= query_date_int."""
        train_dir = settings.ALPHA_TRAIN_DIR
        if not os.path.isdir(train_dir):
            return None

        try:
            files = [f for f in os.listdir(train_dir)
                     if f.startswith("model_de_") and f.endswith(".pkl")]
            model_dates = sorted(
                [int(f.replace("model_de_", "").replace(".pkl", "")) for f in files]
            )
        except Exception:
            return None

        best_date = None
        for md in model_dates:
            if md <= query_date_int:
                best_date = md

        if best_date is None:
            # query date is before all trained models — use earliest
            if model_dates:
                best_date = model_dates[0]
            else:
                return None

        if best_date in self._model_cache:
            return self._model_cache[best_date]

        pkl_path = os.path.join(train_dir, f"model_de_{best_date}.pkl")
        try:
            with open(pkl_path, "rb") as f:
                save_data = pickle.load(f)
            self._model_cache[best_date] = save_data
            log.info("AlphaPredictor: loaded model checkpoint %d", best_date)
            return save_data
        except Exception as e:
            log.warning("AlphaPredictor: failed to load model %d: %s", best_date, e)
            return None

    # ── public API ──────────────────────────────────────────────────────────

    def predict_return(self, query_date: Optional[date] = None, last_price: float = 80.0) -> Optional[float]:
        """
        Predict next-day WTI return for query_date.

        Priority:
        1. Live inference using latest model pkl + data CSV features
        2. Lookup from pre-computed predictions.pkl
        3. Return None (caller falls back to stub)
        """
        if settings.USE_STUB or not self._available:
            return None

        date_int = self._date_to_int(query_date)

        # Try live inference first
        ret = self._live_infer(date_int)
        if ret is not None:
            return ret

        # Fall back to pre-computed predictions
        return self._lookup_prediction(date_int)

    def predict_price(self, query_date: Optional[date] = None, last_price: float = 80.0) -> Optional[float]:
        """Return predicted next-day price (= last_price * (1 + predicted_return))."""
        ret = self.predict_return(query_date, last_price)
        if ret is None:
            return None
        return last_price * (1.0 + ret)

    # ── internal inference ───────────────────────────────────────────────────

    def _live_infer(self, date_int: int) -> Optional[float]:
        """Run live inference using the pkl ensemble model on feature data."""
        if self._data is None:
            return None

        save_data = self._load_model_for_date(date_int)
        if save_data is None:
            return None

        model_list = save_data.get("model_list", [])
        selected_features_list = save_data.get("selected_features_list", [])
        if not model_list:
            return None

        # Use feature_cols from the saved model if available, otherwise derive from CSV
        feature_cols = save_data.get("feature_cols") or [c for c in self._data.columns if c != "label"]
        df = self._data

        if date_int in df.index:
            row = df.loc[date_int, feature_cols]
        else:
            past = df.index[df.index <= date_int]
            if len(past) == 0:
                return None
            row = df.loc[past[-1], feature_cols]

        X = row.values.astype(float).reshape(1, -1)
        if np.isnan(X).any():
            return None

        preds = []
        for model, sel_idx in zip(model_list, selected_features_list):
            try:
                X_sel = X[:, sel_idx]
                # Use the underlying LightGBM Booster directly to avoid sklearn wrapper
                # compatibility issues across LightGBM versions (TypeError in lgb >= 4.0)
                pred = model.booster_.predict(X_sel)
                preds.append(float(pred[0]))
            except Exception:
                pass

        if not preds:
            return None
        return float(np.mean(preds))

    def _lookup_prediction(self, date_int: int) -> Optional[float]:
        """Look up return from pre-computed predictions, using closest past date if exact not found."""
        if not self._predictions:
            return None

        if date_int in self._predictions:
            return self._predictions[date_int]

        # Use the most recent available date
        past_dates = [d for d in sorted(self._predictions.keys()) if d <= date_int]
        if past_dates:
            return self._predictions[past_dates[-1]]

        # query before all predictions — use earliest
        return self._predictions[min(self._predictions.keys())]

    @staticmethod
    def _date_to_int(d: Optional[date]) -> int:
        if d is None:
            from datetime import date as dt_date
            d = dt_date.today()
        if isinstance(d, datetime):
            d = d.date()
        return int(d.strftime("%Y%m%d"))
