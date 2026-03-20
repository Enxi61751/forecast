#!/usr/bin/env bash
# run.sh — Start the model service (port 8000)
# Set USE_STUB=0 and provide model artifact paths to run with real models.
set -e
cd "$(dirname "$0")"
export USE_STUB="${USE_STUB:-1}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
