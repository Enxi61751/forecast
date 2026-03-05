# app/models/lgbm_predictor.py
import numpy as np
from app.config import settings

class LGBMPredictor:
    def __init__(self):
        self._available = False
        self.model = None

        if settings.USE_STUB:
            return

        try:
            import lightgbm as lgb
            self.model = lgb.Booster(model_file=settings.LGBM_MODEL_PATH)
            self._available = True
        except Exception:
            self._available = False

    def predict(self, X: np.ndarray) -> float:
        if settings.USE_STUB or (not self._available):
            # stub：返回一个稳定的“基于最后价格的小偏移”
            return float(X[0, 0])  # 约定 X 第一个特征=last_price

        y = self.model.predict(X)
        return float(y[0])