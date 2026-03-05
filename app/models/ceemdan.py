# app/models/ceemdan.py
from __future__ import annotations

from typing import Optional

import numpy as np

from app.config import settings


class CEEMDANDecomposer:
    def __init__(self):
        self._available: bool = False
        self._CEEMDAN_cls = None  # 保存类，而不是实例

        if getattr(settings, "USE_STUB", False):
            return

        # 尝试导入真实库（PyPI: EMD-signal，导入名是 PyEMD）
        try:
            from PyEMD import CEEMDAN  # type: ignore
            self._CEEMDAN_cls = CEEMDAN
            self._available = True
        except ImportError:
            self._available = False

    def decompose(
        self,
        y: np.ndarray | list[float],
        trials: int = 100,
        noise_width: float = 0.2,
        max_imfs: int = 8,
    ) -> Optional[np.ndarray]:
        """
        Args:
            y: 1D time series (T,)
            trials: CEEMDAN ensemble trials
            noise_width: noise width (depends on implementation)
            max_imfs: keep at most this many IMFs

        Returns:
            imfs: ndarray of shape (n_imfs, T) or None if stub/unavailable
        """
        if getattr(settings, "USE_STUB", False) or (not self._available) or (self._CEEMDAN_cls is None):
            return None

        # 统一输入为 1D float64
        y_arr = np.asarray(y, dtype=np.float64).reshape(-1)
        if y_arr.size < 4:
            # 太短的序列分解意义不大，直接返回 None 或空
            return None

        # 参数兜底
        trials = int(trials) if trials is not None else 100
        trials = max(trials, 1)
        max_imfs = int(max_imfs) if max_imfs is not None else 8
        max_imfs = max(max_imfs, 1)

        # 实例化
        ce = self._CEEMDAN_cls(trials=trials)

        # 兼容不同版本：noise_width 可能是属性或方法
        try:
            setattr(ce, "noise_width", float(noise_width))
        except Exception:
            pass
        if hasattr(ce, "set_noise_width"):
            try:
                ce.set_noise_width(float(noise_width))
            except Exception:
                pass

        # 兼容不同实现：有的用 ce.ceemdan(y)，有的支持 ce(y)
        imfs = None
        if hasattr(ce, "ceemdan"):
            imfs = ce.ceemdan(y_arr)
        else:
            imfs = ce(y_arr)

        imfs = np.asarray(imfs, dtype=np.float64)
        if imfs.ndim != 2:
            return None

        return imfs[:max_imfs]