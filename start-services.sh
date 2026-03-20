#!/usr/bin/env bash
# start-services.sh — Launch model-remote (port 8000) and stagex2 (port 8001)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STAGEX2_DIR=~/stagex2/stagex2/stagex2-source-package/stagex2-source-package

# ── 1. Model Service (model-remote branch, port 8000) ────────────────────────
MODEL_DIR="$SCRIPT_DIR/.model-service"
if [ ! -d "$MODEL_DIR" ]; then
  echo "[model-service] Checking out model-remote branch to $MODEL_DIR ..."
  git -C "$SCRIPT_DIR" worktree add "$MODEL_DIR" model-remote
fi

echo "[model-service] Setting up Python venv ..."
python3 -m venv "$MODEL_DIR/.venv" --quiet
"$MODEL_DIR/.venv/bin/pip" install -q -r "$MODEL_DIR/requirements.txt"

echo "[model-service] Starting on port 8000 ..."
cd "$MODEL_DIR"
"$MODEL_DIR/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 &
MODEL_PID=$!
echo "  PID=$MODEL_PID"
cd "$SCRIPT_DIR"

# ── 2. Agent Service (stagex2, port 8001) ────────────────────────────────────
echo "[agent-service] Setting up Python venv ..."
python3 -m venv "$STAGEX2_DIR/.venv" --quiet
"$STAGEX2_DIR/.venv/bin/pip" install -q -r "$STAGEX2_DIR/requirements.txt"

echo "[agent-service] Starting on port 8001 ..."
cd "$STAGEX2_DIR"
set -a
# shellcheck disable=SC1091
[ -f stagex2.env ] && source stagex2.env
set +a
"$STAGEX2_DIR/.venv/bin/uvicorn" src.stagex2.api:app --host 0.0.0.0 --port 8001 &
AGENT_PID=$!
echo "  PID=$AGENT_PID"
cd "$SCRIPT_DIR"

echo ""
echo "Services started:"
echo "  model-service  → http://localhost:8000  (PID $MODEL_PID)"
echo "  agent-service  → http://localhost:8001  (PID $AGENT_PID)"
echo ""
echo "To stop: kill $MODEL_PID $AGENT_PID"
echo ""
echo "Now start the Spring Boot backend:"
echo "  cd $SCRIPT_DIR && mvn spring-boot:run -Dspring-boot.run.profiles=local"

# Keep script alive so Ctrl-C kills both services
wait $MODEL_PID $AGENT_PID
