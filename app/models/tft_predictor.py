# app/models/tft_predictor.py
<<<<<<< HEAD
import numpy as np
from app.config import settings

=======
from __future__ import annotations

from typing import Any

import numpy as np
from app.config import settings


>>>>>>> c3c3a7b (save local files)
class TFTPredictor:
    def __init__(self):
        self._available = False
        self.model = None
<<<<<<< HEAD
=======
        self.torch = None

        self.quantiles: list[float] | None = None
        self.feature_cols: list[str] = []
        self.known_future_cols: list[str] = []
>>>>>>> c3c3a7b (save local files)

        if settings.USE_STUB:
            return

        try:
            import torch
            self.torch = torch
<<<<<<< HEAD
            self.model = torch.load(settings.TFT_CKPT_PATH, map_location=settings.DEVICE)
            self.model.eval()
            self._available = True
        except Exception:
            self._available = False

    def predict(self, x_seq: np.ndarray) -> dict:
        if settings.USE_STUB or (not self._available):
            # stub：给一个中等风险概率 + 简单预测
            return {"y_hat": np.array([x_seq[0, -1, 0]]), "extreme_prob": np.array([0.5])}

        torch = self.torch
        with torch.no_grad():
            x = torch.tensor(x_seq, dtype=torch.float32, device=settings.DEVICE)
            out = self.model(x)

        # 你们模型输出结构可能不同，这里留适配层
        # 约定 out 是 dict 或 tuple：
        if isinstance(out, dict):
            y_hat = out.get("y_hat")
            extreme_prob = out.get("extreme_prob")
        else:
            y_hat, extreme_prob = out

        return {
            "y_hat": y_hat.detach().cpu().numpy(),
            "extreme_prob": extreme_prob.detach().cpu().numpy()
        }
=======

            ckpt = torch.load(settings.TFT_CKPT_PATH, map_location=settings.DEVICE)

            # 情况1：checkpoint 本身就是一个完整模型对象
            if hasattr(ckpt, "eval") and callable(ckpt.eval):
                self.model = ckpt
                self.model.eval()
                self._available = True
                return

            # 情况2：checkpoint 是一个 dict
            if isinstance(ckpt, dict):
                self.quantiles = self._normalize_quantiles(ckpt.get("quantiles"))
                self.feature_cols = self._normalize_name_list(ckpt.get("feature_cols"))
                self.known_future_cols = self._normalize_name_list(ckpt.get("known_future_cols"))

                # 先尝试从 checkpoint 中直接取模型对象
                maybe_model = ckpt.get("model_obj") or ckpt.get("network") or ckpt.get("module")
                if maybe_model is not None and hasattr(maybe_model, "eval"):
                    self.model = maybe_model
                    self.model.eval()
                    self._available = True
                    return

                # 再尝试重建模型
                rebuilt = self._try_rebuild_model_from_ckpt(ckpt)
                if rebuilt is not None:
                    self.model = rebuilt
                    self.model.eval()
                    self._available = True
                    return

            self._available = False
        except Exception:
            self._available = False

    def _normalize_name_list(self, value: Any) -> list[str]:
        if isinstance(value, (list, tuple)):
            return [str(x) for x in value]
        return []

    def _normalize_quantiles(self, value: Any) -> list[float] | None:
        if isinstance(value, (list, tuple)):
            out = []
            for x in value:
                try:
                    out.append(float(x))
                except Exception:
                    continue
            return out or None
        return None

    def _safe_numpy(self, x: Any) -> np.ndarray:
        if x is None:
            return np.array([], dtype=np.float32)

        if isinstance(x, np.ndarray):
            return x

        torch = self.torch
        if torch is not None and isinstance(x, torch.Tensor):
            return x.detach().cpu().numpy()

        try:
            return np.asarray(x)
        except Exception:
            return np.array([], dtype=np.float32)

    def _safe_float(self, x: Any, default: float = np.nan) -> float:
        try:
            v = float(x)
            if np.isnan(v) or np.isinf(v):
                return default
            return v
        except Exception:
            return default

    def _find_median_index(self, quantiles: list[float] | None, y_hat_np: np.ndarray) -> int:
        if quantiles:
            q_arr = np.asarray(quantiles, dtype=np.float32)
            if q_arr.ndim == 1 and q_arr.size > 0:
                return int(np.argmin(np.abs(q_arr - 0.5)))

        if y_hat_np.ndim >= 2 and y_hat_np.shape[-1] > 1:
            return int(y_hat_np.shape[-1] // 2)

        return 0

    def _try_rebuild_model_from_ckpt(self, ckpt: dict[str, Any]):
        """
        尝试按照你新增源码的思路，从 checkpoint 重建 MultiTaskTFT。
        若当前工程里没有对应类，则自动失败并返回 None，不会让服务崩掉。
        """
        try:
            from app.models.train_tft_multitask import MultiTaskTFT  # type: ignore
        except Exception:
            try:
                # 有些同学会把训练代码不放在 app.models 下，这里再试一次
                from train_tft_multitask import MultiTaskTFT  # type: ignore
            except Exception:
                return None

        try:
            ck_args = ckpt.get("args", {}) or {}
            feature_cols = self._normalize_name_list(ckpt.get("feature_cols"))
            known_future_cols = self._normalize_name_list(ckpt.get("known_future_cols"))
            quantiles = self._normalize_quantiles(ckpt.get("quantiles")) or [0.1, 0.5, 0.9]
            model_state = ckpt.get("model")

            if model_state is None:
                return None

            season_vocab = int(ck_args.get("season_vocab", 1))
            d_model = int(ck_args.get("d_model", 64))
            d_hidden = int(ck_args.get("d_hidden", 128))
            lstm_layers = int(ck_args.get("lstm_layers", 1))
            attn_heads = int(ck_args.get("attn_heads", 4))
            dropout = float(ck_args.get("dropout", 0.1))
            horizon = int(ck_args.get("horizon", 1))

            model = MultiTaskTFT(
                num_hist_features=len(feature_cols) if feature_cols else 1,
                num_known_features=len(known_future_cols),
                season_vocab=season_vocab,
                d_model=d_model,
                d_hidden=d_hidden,
                lstm_layers=lstm_layers,
                attn_heads=attn_heads,
                dropout=dropout,
                horizon=horizon,
                num_quantiles=len(quantiles),
            ).to(settings.DEVICE)

            model.load_state_dict(model_state)
            self.quantiles = quantiles
            self.feature_cols = feature_cols
            self.known_future_cols = known_future_cols
            return model
        except Exception:
            return None

    def _stub_predict(self, x_seq: np.ndarray) -> dict[str, Any]:
        last_val = 0.0
        try:
            last_val = float(x_seq[0, -1, 0])
        except Exception:
            last_val = 0.0

        return {
            "y_hat": np.array([last_val], dtype=np.float32),
            "extreme_prob": np.array([0.5], dtype=np.float32),
            "quantiles": self.quantiles,
            "feature_importance": None,
            "hist_feature_importance": None,
            "known_future_feature_importance": None,
            "raw": {"source": "stub"},
        }

    def _build_feature_importance_from_weights(
        self,
        w_hist: Any,
        w_known: Any,
    ) -> tuple[list[dict[str, Any]] | None, list[dict[str, Any]] | None, list[dict[str, Any]] | None]:
        hist_rows: list[dict[str, Any]] = []
        known_rows: list[dict[str, Any]] = []

        w_hist_np = self._safe_numpy(w_hist)
        w_known_np = self._safe_numpy(w_known)

        # 历史特征权重: 期望 [B, L, F]
        if w_hist_np.size > 0 and w_hist_np.ndim == 3:
            hist_avg = w_hist_np.mean(axis=(0, 1))
            hist_names = self.feature_cols if self.feature_cols else [f"hist_{i}" for i in range(len(hist_avg))]
            for name, w in zip(hist_names, hist_avg):
                val = self._safe_float(w, default=np.nan)
                if np.isfinite(val):
                    hist_rows.append({
                        "feature": str(name),
                        "group": "hist",
                        "avg_weight": float(val),
                    })

        # 已知未来特征权重: 期望 [B, H, K]
        if w_known_np.size > 0 and w_known_np.ndim == 3:
            known_avg = w_known_np.mean(axis=(0, 1))
            known_names = (
                self.known_future_cols
                if self.known_future_cols
                else [f"known_future_{i}" for i in range(len(known_avg))]
            )
            for name, w in zip(known_names, known_avg):
                val = self._safe_float(w, default=np.nan)
                if np.isfinite(val):
                    known_rows.append({
                        "feature": str(name),
                        "group": "known_future",
                        "avg_weight": float(val),
                    })

        hist_rows.sort(key=lambda x: x["avg_weight"], reverse=True)
        known_rows.sort(key=lambda x: x["avg_weight"], reverse=True)

        all_rows = (hist_rows + known_rows) or None
        return all_rows, (hist_rows or None), (known_rows or None)

    def predict(self, x_seq: np.ndarray) -> dict[str, Any]:
        if settings.USE_STUB or (not self._available) or self.model is None:
            return self._stub_predict(x_seq)

        torch = self.torch
        if torch is None:
            return self._stub_predict(x_seq)

        try:
            with torch.no_grad():
                x = torch.tensor(x_seq, dtype=torch.float32, device=settings.DEVICE)

                # 先按你当前旧版接口尝试：model(x)
                out = self.model(x)

            y_hat = None
            extreme_prob = None
            w_hist = None
            w_known = None

            # 1) dict 输出
            if isinstance(out, dict):
                y_hat = out.get("y_hat") or out.get("reg") or out.get("prediction")
                extreme_prob = out.get("extreme_prob") or out.get("prob") or out.get("cls_prob")
                w_hist = out.get("w_hist") or out.get("hist_weights")
                w_known = out.get("w_known") or out.get("known_weights")

            # 2) tuple/list 输出
            elif isinstance(out, (tuple, list)):
                # 兼容:
                # (y_hat, extreme_prob)
                # (reg, cls_logit, w_hist, w_known)
                if len(out) >= 2:
                    y_hat = out[0]
                    extreme_prob = out[1]
                if len(out) >= 4:
                    w_hist = out[2]
                    w_known = out[3]

            else:
                # 3) 其他情况，直接当成 y_hat
                y_hat = out

            if y_hat is None:
                return self._stub_predict(x_seq)

            y_hat_np = self._safe_numpy(y_hat)

            # 统一成至少一维
            if y_hat_np.ndim == 0:
                y_hat_np = y_hat_np.reshape(1)

            # 如果 y_hat 是 [B, Q] 或 [Q]，取中位数分位
            if y_hat_np.ndim == 1:
                median_idx = self._find_median_index(self.quantiles, y_hat_np)
                y_pred_value = y_hat_np[median_idx] if y_hat_np.shape[0] > median_idx else y_hat_np[0]
            else:
                median_idx = self._find_median_index(self.quantiles, y_hat_np)
                y_pred_value = y_hat_np[0, median_idx] if y_hat_np.shape[-1] > median_idx else y_hat_np[0, 0]

            # 分类概率处理
            extreme_prob_np = self._safe_numpy(extreme_prob)
            if extreme_prob_np.size == 0:
                extreme_prob_value = np.array([0.5], dtype=np.float32)
            else:
                # 如果是 logit，尝试做 sigmoid
                try:
                    arr = extreme_prob_np.astype(np.float32)
                    if np.any(arr < 0.0) or np.any(arr > 1.0):
                        arr = 1.0 / (1.0 + np.exp(-arr))
                    extreme_prob_value = np.array([float(arr.reshape(-1)[0])], dtype=np.float32)
                except Exception:
                    extreme_prob_value = np.array([0.5], dtype=np.float32)

            feature_importance, hist_feature_importance, known_future_feature_importance = (
                self._build_feature_importance_from_weights(w_hist, w_known)
            )

            return {
                "y_hat": np.array([self._safe_float(y_pred_value, default=0.0)], dtype=np.float32),
                "extreme_prob": extreme_prob_value,
                "quantiles": self.quantiles,
                "feature_importance": feature_importance,
                "hist_feature_importance": hist_feature_importance,
                "known_future_feature_importance": known_future_feature_importance,
                "raw": {
                    "has_w_hist": w_hist is not None,
                    "has_w_known": w_known is not None,
                    "source": "real_tft",
                },
            }
        except Exception:
            return self._stub_predict(x_seq)
>>>>>>> c3c3a7b (save local files)
