#!/usr/bin/env bash
# start-services.sh — Launch model-remote (port 8000) and stagex2 (port 8001)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$SCRIPT_DIR/agent-service"

# ── 1. Model Service (model-remote branch, port 8000) ────────────────────────
# MODEL_DIR: path to the ~/model directory containing ML artifacts
# MODEL_SVC_DIR: git worktree checkout of model-remote branch
export MODEL_DIR="${MODEL_DIR:-$HOME/model}"
MODEL_SVC_DIR="$SCRIPT_DIR/.model-service"
if [ ! -d "$MODEL_SVC_DIR" ]; then
  echo "[model-service] Checking out model-remote branch to $MODEL_SVC_DIR ..."
  git -C "$SCRIPT_DIR" worktree add "$MODEL_SVC_DIR" model-remote
fi

echo "[model-service] Setting up Python venv ..."
python3 -m venv "$MODEL_SVC_DIR/.venv"
"$MODEL_SVC_DIR/.venv/bin/pip" install -q -r "$MODEL_SVC_DIR/requirements.txt"

echo "[model-service] Starting on port 8000 (MODEL_DIR=$MODEL_DIR) ..."
cd "$MODEL_SVC_DIR"
MODEL_DIR="$MODEL_DIR" "$MODEL_SVC_DIR/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 &
MODEL_PID=$!
echo "  PID=$MODEL_PID"
cd "$SCRIPT_DIR"

# ── 2. Agent Service (agent-service/, port 8001) ─────────────────────────────
echo "[agent-service] Setting up Python venv ..."
python3 -m venv "$AGENT_DIR/.venv"
"$AGENT_DIR/.venv/bin/pip" install -q -r "$AGENT_DIR/requirements.txt"

echo "[agent-service] Starting on port 8001 ..."
cd "$AGENT_DIR"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
set +a
"$AGENT_DIR/.venv/bin/uvicorn" src.stagex2.api:app --host 0.0.0.0 --port 8001 &
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
