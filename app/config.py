# app/config.py
from pydantic import BaseModel
import os

class Settings(BaseModel):
    # 运行模式：1=stub（模型没好也能跑），0=real
    USE_STUB: bool = os.getenv("USE_STUB", "1") == "1"

    # 模型文件路径（模型组交付后替换/挂载）
    LGBM_MODEL_PATH: str = os.getenv("LGBM_MODEL_PATH", "artifacts/lgbm_model.txt")
    TFT_CKPT_PATH: str = os.getenv("TFT_CKPT_PATH", "artifacts/tft_ckpt.pt")

    # TFT 运行设备
    DEVICE: str = os.getenv("DEVICE", "cpu")

settings = Settings()