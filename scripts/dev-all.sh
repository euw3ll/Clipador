#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
export PYTHONPATH="$ROOT_DIR/packages/clipador-core/src:$ROOT_DIR/packages/clipador-adapters/src"
BACKEND_ENV="$ROOT_DIR/services/backend/.env"
UVICORN_BIN="$ROOT_DIR/.venv/bin/uvicorn"
CELERY_BIN="$ROOT_DIR/.venv/bin/celery"
mkdir -p "$ROOT_DIR/.uv-cache"

set -a
source "$BACKEND_ENV"
set +a

API_CMD=("$UVICORN_BIN" clipador_backend.main:app \
  --app-dir "$ROOT_DIR/services/backend/src" \
  --env-file "$BACKEND_ENV")

WORKER_CMD=("$CELERY_BIN" -A clipador_backend.celery_app worker --loglevel=info)

BEAT_CMD=("$CELERY_BIN" -A clipador_backend.celery_app beat --loglevel=info)

echo "[dev-all] Starting API..."
"${API_CMD[@]}" & API_PID=$!
sleep 1

echo "[dev-all] Starting worker..."
"${WORKER_CMD[@]}" & WORKER_PID=$!
sleep 1

echo "[dev-all] Starting beat..."
"${BEAT_CMD[@]}" & BEAT_PID=$!

echo "[dev-all] PIDs -> API: $API_PID  WORKER: $WORKER_PID  BEAT: $BEAT_PID"
echo "[dev-all] Press Ctrl+C to stop all"

cleanup() {
  echo "\n[dev-all] Stopping..."
  kill $API_PID $WORKER_PID $BEAT_PID 2>/dev/null || true
  wait $API_PID $WORKER_PID $BEAT_PID 2>/dev/null || true
  echo "[dev-all] Done."
}

trap cleanup INT TERM
wait $API_PID $WORKER_PID $BEAT_PID || true
