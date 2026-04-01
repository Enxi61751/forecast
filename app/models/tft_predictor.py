from __future__ import annotations

from typing import Any

import numpy as np

from app.config import settings


class TFTPredictor:
    def __init__(self):
        self._available = False
        self.model = None
        self.torch = None

        self.quantiles: list[float] | None = None
        self.feature_cols: list[str] = []
        self.known_future_cols: list[str] = []

        if settings.USE_STUB:
            return

        try:
            import torch

            self.torch = torch
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
        尝试从 checkpoint 重建 MultiTaskTFT。
        若当前工程里没有对应类，则返回 None。
        """
        try:
            from app.models.train_tft_multitask import MultiTaskTFT  # type: ignore
        except Exception:
            try:
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
            "y_hat": float(last_val),
            "extreme_prob": 0.5,
            "quantiles": [float(q) for q in self.quantiles] if self.quantiles else None,
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
                    hist_rows.append(
                        {
                            "feature": str(name),
                            "group": "hist",
                            "avg_weight": float(val),
                        }
                    )

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
                    known_rows.append(
                        {
                            "feature": str(name),
                            "group": "known_future",
                            "avg_weight": float(val),
                        }
                    )

        hist_rows.sort(key=lambda x: x["avg_weight"], reverse=True)
        known_rows.sort(key=lambda x: x["avg_weight"], reverse=True)

        all_rows = (hist_rows + known_rows) or None
        return all_rows, (hist_rows or None), (known_rows or None)

    def _call_model(self, x_seq: np.ndarray):
        """
        尽量兼容多种 forward 签名：
        1) model(x)
        2) model(x_hist, x_known, season_id)
        """
        torch = self.torch
        if torch is None:
            return None

        x = torch.tensor(x_seq, dtype=torch.float32, device=settings.DEVICE)

        # 方案1：单输入接口
        try:
            return self.model(x)
        except TypeError:
            pass
        except Exception:
            pass

        # 方案2：多输入接口（参考离线评估脚本）
        try:
            batch_size = x.shape[0]
            lookback = x.shape[1] if x.ndim >= 2 else 1

            # 当前在线服务没有 known future / season_id 真值，只做最小兼容占位
            x_hist = x
            x_known = torch.zeros((batch_size, 1, max(len(self.known_future_cols), 1)), dtype=torch.float32, device=settings.DEVICE)
            season_id = torch.zeros((batch_size,), dtype=torch.long, device=settings.DEVICE)

            return self.model(x_hist, x_known, season_id)
        except Exception:
            return None

    def predict(self, x_seq: np.ndarray) -> dict[str, Any]:
        if settings.USE_STUB or (not self._available) or self.model is None:
            return self._stub_predict(x_seq)

        torch = self.torch
        if torch is None:
            return self._stub_predict(x_seq)

        try:
            with torch.no_grad():
                out = self._call_model(x_seq)

            if out is None:
                return self._stub_predict(x_seq)

            y_hat = None
            extreme_prob = None
            w_hist = None
            w_known = None

            # 1) dict 输出
            if isinstance(out, dict):
                y_hat = out.get("y_hat") or out.get("reg") or out.get("prediction")
                extreme_prob = (
                    out.get("extreme_prob")
                    or out.get("prob")
                    or out.get("cls_prob")
                    or out.get("cls")
                )
                w_hist = out.get("w_hist") or out.get("hist_weights")
                w_known = out.get("w_known") or out.get("known_weights")

            # 2) tuple/list 输出：兼容 (reg, cls_logit, w_hist, w_known)
            elif isinstance(out, (tuple, list)):
                if len(out) >= 1:
                    y_hat = out[0]
                if len(out) >= 2:
                    extreme_prob = out[1]
                if len(out) >= 3:
                    w_hist = out[2]
                if len(out) >= 4:
                    w_known = out[3]

            # 3) 其他情况：直接当 y_hat
            else:
                y_hat = out

            if y_hat is None:
                return self._stub_predict(x_seq)

            # ---------- 1. 处理 y_hat ----------
            y_hat_np = self._safe_numpy(y_hat)
            if y_hat_np.size == 0:
                return self._stub_predict(x_seq)

            if y_hat_np.ndim == 0:
                y_hat_np = y_hat_np.reshape(1)

            # [Q] or [1,Q] -> 取最接近 0.5 的分位
            if y_hat_np.ndim == 1:
                median_idx = self._find_median_index(self.quantiles, y_hat_np)
                y_pred_value = y_hat_np[median_idx] if y_hat_np.shape[0] > median_idx else y_hat_np[0]
            else:
                median_idx = self._find_median_index(self.quantiles, y_hat_np)
                y_pred_value = y_hat_np[0, median_idx] if y_hat_np.shape[-1] > median_idx else y_hat_np.reshape(-1)[0]

            # ---------- 2. 处理 extreme_prob ----------
            extreme_prob_np = self._safe_numpy(extreme_prob)
            if extreme_prob_np.size == 0:
                extreme_prob_scalar = 0.5
            else:
                try:
                    arr = extreme_prob_np.astype(np.float32)

                    # 若拿到的是 cls_logit，则转 sigmoid
                    if np.any(arr < 0.0) or np.any(arr > 1.0):
                        arr = 1.0 / (1.0 + np.exp(-arr))

                    extreme_prob_scalar = float(arr.reshape(-1)[0])
                except Exception:
                    extreme_prob_scalar = 0.5

            # ---------- 3. 处理特征重要性 ----------
            feature_importance, hist_feature_importance, known_future_feature_importance = (
                self._build_feature_importance_from_weights(w_hist, w_known)
            )

            # ---------- 4. 返回 JSON-safe 结构 ----------
            return {
                "y_hat": float(self._safe_float(y_pred_value, default=0.0)),
                "extreme_prob": float(extreme_prob_scalar),
                "quantiles": [float(q) for q in self.quantiles] if self.quantiles else None,
                "feature_importance": feature_importance,
                "hist_feature_importance": hist_feature_importance,
                "known_future_feature_importance": known_future_feature_importance,
                "raw": {
                    "source": "real_tft",
                    "has_w_hist": bool(w_hist is not None),
                    "has_w_known": bool(w_known is not None),
                },
            }
        except Exception:
            return self._stub_predict(x_seq)