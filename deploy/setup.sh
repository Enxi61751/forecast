#!/bin/bash
# setup.sh — First-time server setup (run once after git clone)
set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)

echo "==> Setting up model-service (model-remote branch)..."
if [ ! -d "$ROOT/model-service" ]; then
  git worktree add model-service model-remote
fi
cp deploy/model-service/Dockerfile model-service/Dockerfile

echo "==> Setting up frontend (frontend-iteration-2 branch)..."
if [ ! -d "$ROOT/frontend-src" ]; then
  git worktree add frontend-src frontend-iteration-2
fi
cp deploy/frontend/Dockerfile frontend-src/frontend/Dockerfile

echo "==> Creating model-artifacts directory..."
mkdir -p model-artifacts

echo "==> Creating .env from template..."
if [ ! -f "$ROOT/.env" ]; then
  cp .env.example .env
  echo "    Created .env — please edit it and fill in your real keys:"
  echo "    vim $ROOT/.env"
else
  echo "    .env already exists, skipping"
fi

echo ""
echo "==> Setup complete! Next steps:"
echo "  1. Upload ML model files to $ROOT/model-artifacts/"
echo "  2. Edit $ROOT/.env with real keys"
echo "  3. Run: docker compose build"
echo "  4. Run: docker compose up -d"
