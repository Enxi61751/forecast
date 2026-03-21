# app/models/tft_csv_predictor.py
"""
TFT lookup predictor using pre-computed predictions CSV.

The TFT model (~/model/TFT/) outputs predictions into:
    gbo_tft_test_predictions_cl0_1d_close_smooth_latest.csv

Columns: date, y_true, y_pred, lower_60, upper_60, lower_70, upper_70,
         lower_80, upper_80, lower_90, upper_90

We load this CSV and serve predictions as a lookup table.
For dates beyond the CSV range, we return the most recent available entry.
"""
from __future__ import annotations

import os
import logging
from datetime import date, datetime
from typing import Optional

import numpy as np

from app.config import settings

log = logging.getLogger(__name__)


class TFTCSVPredictor:
    """Serves TFT predictions from the pre-computed CSV file."""

    def __init__(self):
        self._available = False
        self._df = None

        if settings.USE_STUB:
            return

        self._load_csv()

    def _load_csv(self):
        path = settings.TFT_PREDICTIONS_CSV
        if not os.path.isfile(path):
            log.warning("TFTCSVPredictor: predictions CSV not found at %s", path)
            return
        try:
            import pandas as pd
            df = pd.read_csv(path, parse_dates=["date"])
            df = df.sort_values("date").reset_index(drop=True)
            self._df = df
            self._available = True
            log.info("TFTCSVPredictor: loaded %d TFT predictions from %s", len(df), path)
        except Exception as e:
            log.warning("TFTCSVPredictor: failed to load CSV: %s", e)

    def predict(self, query_date: Optional[date] = None) -> dict:
        """
        Return prediction dict for query_date.
        Keys: y_pred, lower_90, upper_90 (NaN-safe floats)
        Falls back to last available row if date not found.
        """
        if settings.USE_STUB or not self._available or self._df is None:
            return {"y_pred": np.nan, "lower_90": np.nan, "upper_90": np.nan}

        if query_date is None:
            from datetime import date as dt_date
            query_date = dt_date.today()
        if isinstance(query_date, datetime):
            query_date = query_date.date()

        import pandas as pd
        target_ts = pd.Timestamp(query_date)
        df = self._df

        # exact match
        exact = df[df["date"] == target_ts]
        if not exact.empty:
            row = exact.iloc[0]
        else:
            past = df[df["date"] <= target_ts]
            if past.empty:
                row = df.iloc[0]
            else:
                row = past.iloc[-1]

        def _safe(col: str) -> float:
            if col not in row.index:
                return np.nan
            v = row[col]
            try:
                v = float(v)
            except Exception:
                v = np.nan
            return v

        return {
            "y_pred": _safe("y_pred"),
            "lower_90": _safe("lower_90"),
            "upper_90": _safe("upper_90"),
            "lower_80": _safe("lower_80"),
            "upper_80": _safe("upper_80"),
        }
