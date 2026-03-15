# app/models/ceemdan.py
from __future__ import annotations

from typing import Any, Optional

import numpy as np

from app.config import settings


class CEEMDANDecomposer:
    def __init__(self):
        self._available: bool = False
        self._CEEMDAN_cls = None
        self._sample_entropy_func = None

        if getattr(settings, "USE_STUB", False):
            return

        # CEEMDAN: pip install EMD-signal
        try:
            from PyEMD import CEEMDAN  # type: ignore
            self._CEEMDAN_cls = CEEMDAN
            self._available = True
        except ImportError:
            self._available = False

        # antropy: pip install antropy
        try:
            import antropy as ant  # type: ignore
            self._sample_entropy_func = ant.sample_entropy
        except ImportError:
            self._sample_entropy_func = None

    @property
    def available(self) -> bool:
        return self._available and (self._CEEMDAN_cls is not None)

    def _to_1d_array(self, y: np.ndarray | list[float]) -> np.ndarray:
        y_arr = np.asarray(y, dtype=np.float64).reshape(-1)
        return y_arr

    def _safe_normalize(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64).reshape(-1)
        x_min = np.min(x)
        x_max = np.max(x)
        denom = x_max - x_min
        if denom < 1e-12:
            return np.zeros_like(x, dtype=np.float64)
        return (x - x_min) / (denom + 1e-6)

    def _sample_entropy(self, x: np.ndarray) -> float:
        """
        优先使用 antropy.sample_entropy；
        若 antropy 不可用或计算失败，则返回 0.0。
        """
        if self._sample_entropy_func is None:
            return 0.0

        x_norm = self._safe_normalize(x)
        try:
            val = self._sample_entropy_func(x_norm)
            if val is None or not np.isfinite(val):
                return 0.0
            return float(val)
        except Exception:
            return 0.0

    def _build_instance(
        self,
        trials: int,
        noise_width: float,
        seed: Optional[int] = 42,
    ):
        """
        尽量兼容不同版本的 PyEMD.CEEMDAN。
        你给的源码里主要用了:
            ceemdan = CEEMDAN(trials=100)
            imfs = ceemdan(series)
            res = ceemdan.residue
        :contentReference[oaicite:2]{index=2}
        """
        ce = self._CEEMDAN_cls(trials=trials)

        # 不同版本可能叫 noise_width / epsilon / set_noise_width
        try:
            setattr(ce, "noise_width", float(noise_width))
        except Exception:
            pass

        try:
            setattr(ce, "epsilon", float(noise_width))
        except Exception:
            pass

        if hasattr(ce, "set_noise_width"):
            try:
                ce.set_noise_width(float(noise_width))
            except Exception:
                pass

        if seed is not None:
            if hasattr(ce, "noise_seed"):
                try:
                    ce.noise_seed(int(seed))
                except Exception:
                    pass
            elif hasattr(ce, "seed"):
                try:
                    ce.seed(int(seed))
                except Exception:
                    pass

        return ce

    def decompose(
        self,
        y: np.ndarray | list[float],
        trials: int = 100,
        noise_width: float = 0.2,
        max_imfs: int = 8,
        include_residue: bool = False,
        merge_residue_to_last: bool = False,
        seed: Optional[int] = 42,
    ) -> Optional[np.ndarray]:
        """
        基础分解接口，保持和你当前框架尽量一致。

        Args:
            y: 1D time series (T,)
            trials: CEEMDAN ensemble trials
            noise_width: noise width / epsilon
            max_imfs: keep at most this many IMFs
            include_residue: 是否把 residue 作为最后一行一起返回
            merge_residue_to_last: 是否把 residue 并入最后一个 IMF
            seed: 随机种子

        Returns:
            ndarray:
                - 默认返回 shape (n_imfs, T)
                - include_residue=True 时返回 shape (n_imfs+1, T)
            或 None
        """
        if getattr(settings, "USE_STUB", False) or (not self.available):
            return None

        y_arr = self._to_1d_array(y)
        if y_arr.size < 4:
            return None
        if not np.all(np.isfinite(y_arr)):
            return None

        trials = max(int(trials) if trials is not None else 100, 1)
        max_imfs = max(int(max_imfs) if max_imfs is not None else 8, 1)

        ce = self._build_instance(
            trials=trials,
            noise_width=noise_width,
            seed=seed,
        )

        # 兼容不同调用方式：你给的源码实际用了 ceemdan(series) :contentReference[oaicite:3]{index=3}
        try:
            if hasattr(ce, "ceemdan"):
                imfs = ce.ceemdan(y_arr)
            else:
                imfs = ce(y_arr)
        except Exception:
            return None

        imfs = np.asarray(imfs, dtype=np.float64)
        if imfs.ndim != 2 or imfs.shape[1] != y_arr.shape[0]:
            return None

        residue = None
        if hasattr(ce, "residue"):
            try:
                residue = np.asarray(ce.residue, dtype=np.float64).reshape(-1)
                if residue.shape[0] != y_arr.shape[0]:
                    residue = None
            except Exception:
                residue = None

        # 截断 IMF 数量
        imfs = imfs[:max_imfs]

        # 按 ceemdan_combine 的思路，可把极小残差并入最后一层趋势项
        # imfs[-1] = imfs[-1] + res  :contentReference[oaicite:4]{index=4}
        if merge_residue_to_last and residue is not None and imfs.shape[0] > 0:
            imfs = imfs.copy()
            imfs[-1] = imfs[-1] + residue
            residue = None

        if include_residue and residue is not None:
            return np.vstack([imfs, residue])

        return imfs

    def decompose_full(
        self,
        y: np.ndarray | list[float],
        trials: int = 100,
        noise_width: float = 0.2,
        max_imfs: int = 8,
        seed: Optional[int] = 42,
    ) -> Optional[dict[str, Any]]:
        """
        返回更完整的信息，适合 pipeline / API 层使用。
        """
        if getattr(settings, "USE_STUB", False) or (not self.available):
            return None

        y_arr = self._to_1d_array(y)
        if y_arr.size < 4:
            return None
        if not np.all(np.isfinite(y_arr)):
            return None

        trials = max(int(trials) if trials is not None else 100, 1)
        max_imfs = max(int(max_imfs) if max_imfs is not None else 8, 1)

        ce = self._build_instance(
            trials=trials,
            noise_width=noise_width,
            seed=seed,
        )

        try:
            if hasattr(ce, "ceemdan"):
                imfs = ce.ceemdan(y_arr)
            else:
                imfs = ce(y_arr)
        except Exception:
            return None

        imfs = np.asarray(imfs, dtype=np.float64)
        if imfs.ndim != 2 or imfs.shape[1] != y_arr.shape[0]:
            return None

        imfs = imfs[:max_imfs]

        residue = None
        if hasattr(ce, "residue"):
            try:
                residue = np.asarray(ce.residue, dtype=np.float64).reshape(-1)
                if residue.shape[0] != y_arr.shape[0]:
                    residue = None
            except Exception:
                residue = None

        entropies = [self._sample_entropy(imfs[i]) for i in range(imfs.shape[0])]

        return {
            "original": y_arr,
            "imfs": imfs,
            "residue": residue,
            "n_imfs": int(imfs.shape[0]),
            "length": int(imfs.shape[1]),
            "entropies": np.asarray(entropies, dtype=np.float64),
        }

    def classify_components(
        self,
        y: np.ndarray | list[float],
        trials: int = 100,
        noise_width: float = 0.2,
        max_imfs: int = 8,
        seed: Optional[int] = 42,
    ) -> Optional[dict[str, Any]]:
        """
        按你给的 ceemdan_combine.py 思路做四类聚合:
            1. Random = IMF1
            2. Shock = IMF2 + IMF3
            3. Cyclic = IMF4 + IMF5 + IMF6 + IMF7
            4. Trend = IMF8及以后（若不足则最后一个 IMF）
        其中源码还把 residue 并入最后一层趋势项。:contentReference[oaicite:5]{index=5}
        """
        result = self.decompose_full(
            y=y,
            trials=trials,
            noise_width=noise_width,
            max_imfs=max_imfs,
            seed=seed,
        )
        if result is None:
            return None

        imfs = np.asarray(result["imfs"], dtype=np.float64)
        residue = result["residue"]
        if residue is not None and imfs.shape[0] > 0:
            imfs = imfs.copy()
            imfs[-1] = imfs[-1] + residue

        n_imfs, T = imfs.shape

        zeros = np.zeros(T, dtype=np.float64)

        # Random: IMF1
        random_comp = imfs[0].copy() if n_imfs >= 1 else zeros.copy()

        # Shock: IMF2 + IMF3
        if n_imfs >= 3:
            shock_comp = np.sum(imfs[1:3], axis=0)
        elif n_imfs == 2:
            shock_comp = imfs[1].copy()
        else:
            shock_comp = zeros.copy()

        # Cyclic: IMF4 ~ IMF7
        if n_imfs >= 7:
            cyclic_comp = np.sum(imfs[3:7], axis=0)
        elif n_imfs >= 4:
            cyclic_comp = np.sum(imfs[3:n_imfs], axis=0)
        else:
            cyclic_comp = zeros.copy()

        # Trend: IMF8及以后；若不足8层则取最后一层
        if n_imfs > 7:
            trend_comp = np.sum(imfs[7:], axis=0)
        elif n_imfs >= 1:
            trend_comp = imfs[-1].copy()
        else:
            trend_comp = zeros.copy()

        return {
            "original": np.asarray(result["original"], dtype=np.float64),
            "imfs": imfs,
            "n_imfs": int(n_imfs),
            "length": int(T),
            "entropies": np.asarray(
                [self._sample_entropy(imfs[i]) for i in range(n_imfs)],
                dtype=np.float64,
            ),
            "random_component": random_comp,
            "shock_component": shock_comp,
            "cyclic_component": cyclic_comp,
            "trend_component": trend_comp,
        }