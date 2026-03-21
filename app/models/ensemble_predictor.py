# app/models/ensemble_predictor.py
"""
Ensemble predictor that combines AlphaModelFrame + TFT predictions using
pre-computed MWUM weights from the ensemble output CSV.

The ensemble CSV (~/model/ensemble/output/ensemble.csv) contains:
    date, true_y, GBO_Prediction, Tree_Prediction, weight_1, weight_2,
    eta_used, Ensemble_Prediction

We read the last row to get current stable weights and apply them to
live predictions from AlphaPredictor and TFTCSVPredictor.
"""
from __future__ import annotations

import os
import logging
from datetime import date, datetime
from typing import Optional, Tuple

import numpy as np

from app.config import settings
from app.models.alpha_predictor import AlphaPredictor
from app.models.tft_csv_predictor import TFTCSVPredictor

log = logging.getLogger(__name__)


class EnsemblePredictor:
    def __init__(self):
        self.alpha = AlphaPredictor()
        self.tft = TFTCSVPredictor()
        self._w1: float = 0.5   # weight for AlphaModelFrame (GBO)
        self._w2: float = 0.5   # weight for TFT (Tree)
        self._load_weights()

    def _load_weights(self):
        path = settings.ENSEMBLE_CSV
        if not os.path.isfile(path):
            log.info("EnsemblePredictor: ensemble CSV not found, using equal weights")
            return
        try:
            import pandas as pd
            df = pd.read_csv(path, parse_dates=["date"])
            last = df.iloc[-1]
            w1 = float(last.get("weight_1", 0.5))
            w2 = float(last.get("weight_2", 0.5))
            total = w1 + w2
            if total > 0:
                self._w1 = w1 / total
                self._w2 = w2 / total
            log.info("EnsemblePredictor: weights loaded — alpha=%.3f, tft=%.3f", self._w1, self._w2)
        except Exception as e:
            log.warning("EnsemblePredictor: failed to load weights: %s", e)

    def predict(
        self,
        query_date: Optional[date] = None,
        last_price: float = 80.0,
    ) -> Tuple[float, float, float, dict]:
        """
        Returns (point_pred, lower_90, upper_90, explain_dict).

        Strategy:
        - AlphaPredictor: predicts next-day return → convert to price
        - TFTCSVPredictor: lookup price prediction with CI
        - Blend using MWUM weights from ensemble CSV
        """
        if query_date is None:
            from datetime import date as dt_date
            query_date = dt_date.today()
        if isinstance(query_date, datetime):
            query_date = query_date.date()

        # Alpha prediction
        alpha_price = self.alpha.predict_price(query_date, last_price)

        # TFT prediction
        tft_out = self.tft.predict(query_date)
        tft_price = tft_out.get("y_pred", np.nan)
        lower_90 = tft_out.get("lower_90", np.nan)
        upper_90 = tft_out.get("upper_90", np.nan)

        # Ensemble blend
        has_alpha = alpha_price is not None and np.isfinite(alpha_price)
        has_tft = tft_price is not None and np.isfinite(tft_price)

        if has_alpha and has_tft:
            point = self._w1 * alpha_price + self._w2 * tft_price
        elif has_alpha:
            point = alpha_price
            lower_90 = alpha_price * 0.97
            upper_90 = alpha_price * 1.03
        elif has_tft:
            point = tft_price
        else:
            point = last_price  # ultimate fallback

        # Adjust CIs if missing
        if not np.isfinite(lower_90):
            lower_90 = point * 0.97
        if not np.isfinite(upper_90):
            upper_90 = point * 1.03

        explain = {
            "alpha_price": alpha_price,
            "tft_price": tft_price if has_tft else None,
            "weight_alpha": self._w1,
            "weight_tft": self._w2,
        }

        return float(point), float(lower_90), float(upper_90), explain
