# app/config.py
from pydantic import BaseModel
import os

_home = os.path.expanduser("~")
_default_model_dir = os.path.join(_home, "model")

class Settings(BaseModel):
    # 运行模式：0=real models, 1=stub fallback
    # Auto-set to 0 when MODEL_DIR exists; override with USE_STUB env var
    USE_STUB: bool = os.getenv("USE_STUB", "0" if os.path.isdir(os.getenv("MODEL_DIR", _default_model_dir)) else "1") == "1"

    # Root directory of the ~/model folder
    MODEL_DIR: str = os.getenv("MODEL_DIR", _default_model_dir)

    # AlphaModelFrame paths (derived from MODEL_DIR)
    ALPHA_TRAIN_DIR: str = os.getenv(
        "ALPHA_TRAIN_DIR",
        os.path.join(_default_model_dir,
                     "AlphaModelFrame/Output/Model_File/"
                     "Model-DE_GS-u30-l240-p1-dataset_wti_return_new/model_train")
    )
    ALPHA_PREDICTIONS_PKL: str = os.getenv(
        "ALPHA_PREDICTIONS_PKL",
        os.path.join(_default_model_dir,
                     "AlphaModelFrame/Output/Model_File/"
                     "Model-DE_GS-u30-l240-p1-dataset_wti_return_new/model_infer/predictions.pkl")
    )
    ALPHA_DATA_CSV: str = os.getenv(
        "ALPHA_DATA_CSV",
        os.path.join(_default_model_dir,
                     "AlphaModelFrame/Data/dataset_wti_return_new.csv")
    )

    # TFT pre-computed predictions CSV (used as lookup since no checkpoint saved)
    TFT_PREDICTIONS_CSV: str = os.getenv(
        "TFT_PREDICTIONS_CSV",
        os.path.join(_default_model_dir,
                     "TFT/gbo_tft_test_predictions_cl0_1d_close_smooth_latest.csv")
    )

    # Ensemble output (final combined predictions)
    ENSEMBLE_CSV: str = os.getenv(
        "ENSEMBLE_CSV",
        os.path.join(_default_model_dir, "ensemble/output/ensemble.csv")
    )

    # Legacy paths (kept for backward compat, not used when real models are available)
    LGBM_MODEL_PATH: str = os.getenv("LGBM_MODEL_PATH", "artifacts/lgbm_model.txt")
    TFT_CKPT_PATH: str = os.getenv("TFT_CKPT_PATH", "artifacts/tft_ckpt.pt")
    DEVICE: str = os.getenv("DEVICE", "cpu")

settings = Settings()
