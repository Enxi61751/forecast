# app/models/tft_predictor.py
import numpy as np
from app.config import settings

class TFTPredictor:
    def __init__(self):
        self._available = False
        self.model = None

        if settings.USE_STUB:
            return

        try:
            import torch
            self.torch = torch
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