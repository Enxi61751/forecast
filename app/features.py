# app/features.py
from __future__ import annotations

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

def build_tabular_features(
    y: np.ndarray,
    imfs: Optional[np.ndarray],
    indicators_last: Dict[str, float],
    sentiment_last: Optional[float],
    events: list,
) -> Tuple[np.ndarray, Dict]:
    last_price = float(y[-1])
    ret1 = float((y[-1] - y[-2]) / (y[-2] + 1e-9)) if len(y) >= 2 else 0.0

    feats = {
        "last_price": last_price,
        "ret1": ret1,
    }

    # indicators
    for k, v in indicators_last.items():
        feats[f"ind_{k}_last"] = float(v)

    if sentiment_last is not None:
        feats["sent_last"] = float(sentiment_last)

    # events: last 7 days count + max intensity（示例）
    feats["evt_cnt_7d"] = float(len(events))
    feats["evt_max_intensity_7d"] = float(max([e.intensity for e in events], default=0.0))

    # CEEMDAN imfs stats
    if imfs is not None:
        for i in range(imfs.shape[0]):
            feats[f"imf{i}_last"] = float(imfs[i, -1])
            feats[f"imf{i}_mean7"] = float(imfs[i, -7:].mean()) if imfs.shape[1] >= 7 else float(imfs[i].mean())

    # 转成 np array（固定顺序很重要！）
    feature_order = list(feats.keys())
    X = np.array([[feats[k] for k in feature_order]], dtype=float)
    meta = {"feature_order": feature_order}
    return X, meta

def build_sequence_features(y: np.ndarray, window: int = 60) -> np.ndarray:
    """
    简化：只用 price 序列做 TFT 输入的第一个通道
    真实版本：拼上 indicators/sentiment 等多维特征
    """
    w = min(window, len(y))
    seq = y[-w:]
    # (1, T, F) 这里 F=1
    return seq.reshape(1, w, 1).astype(float)