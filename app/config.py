# app/config.py
from pydantic import BaseModel
import os

_home = os.path.expanduser("~")
_default_model_dir = os.path.join(_home, "model")

# Resolve MODEL_DIR at import time so all derived paths are consistent
_model_dir = os.getenv("MODEL_DIR", _default_model_dir)

def _model_path(*parts: str) -> str:
    """Build a path under MODEL_DIR, overridable via env var."""
    return os.path.join(_model_dir, *parts)


class Settings(BaseModel):
    # Run mode: 0=real models, 1=stub fallback
    # Auto-set to 0 when MODEL_DIR exists; override with USE_STUB env var
    USE_STUB: bool = os.getenv("USE_STUB", "0" if os.path.isdir(_model_dir) else "1") == "1"

    # Root directory of the ~/model folder
    MODEL_DIR: str = _model_dir

    # AlphaModelFrame paths
    ALPHA_TRAIN_DIR: str = os.getenv(
        "ALPHA_TRAIN_DIR",
        _model_path("AlphaModelFrame/Output/Model_File/"
                    "Model-DE_GS-u30-l240-p1-dataset_wti_return_new/model_train")
    )
    ALPHA_PREDICTIONS_PKL: str = os.getenv(
        "ALPHA_PREDICTIONS_PKL",
        _model_path("AlphaModelFrame/Output/Model_File/"
                    "Model-DE_GS-u30-l240-p1-dataset_wti_return_new/model_infer/predictions.pkl")
    )
    ALPHA_DATA_CSV: str = os.getenv(
        "ALPHA_DATA_CSV",
        _model_path("AlphaModelFrame/Data/dataset_wti_return_new.csv")
    )

    # TFT pre-computed predictions CSV
    TFT_PREDICTIONS_CSV: str = os.getenv(
        "TFT_PREDICTIONS_CSV",
        _model_path("TFT/gbo_tft_test_predictions_cl0_1d_close_smooth_latest.csv")
    )

    # Ensemble output (final combined predictions with MWUM weights)
    ENSEMBLE_CSV: str = os.getenv(
        "ENSEMBLE_CSV",
        _model_path("ensemble/output/ensemble.csv")
    )

    # Legacy artifact paths (kept for backward compat)
    LGBM_MODEL_PATH: str = os.getenv("LGBM_MODEL_PATH", "artifacts/lgbm_model.txt")
    TFT_CKPT_PATH: str = os.getenv("TFT_CKPT_PATH", "artifacts/tft_ckpt.pt")
    DEVICE: str = os.getenv("DEVICE", "cpu")

settings = Settings()
