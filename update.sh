#!/bin/bash
# update.sh — Pull latest code and rebuild all services
set -e
cd "$(dirname "$0")"

echo "==> Pulling latest code..."
git pull

echo "==> Pulling model-service (model-remote branch)..."
cd model-service && git pull && cd ..

echo "==> Pulling frontend..."
cd frontend && git pull && cd ..

echo "==> Rebuilding and restarting services..."
docker compose build
docker compose up -d

echo "==> Done! Checking service status..."
docker compose ps
