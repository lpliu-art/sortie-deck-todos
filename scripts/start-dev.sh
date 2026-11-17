#!/usr/bin/env bash
# Start Sortie Deck API + workbench (local production-like).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "created .env from .env.example"
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -e ".[dev,docs]"
fi

# shellcheck disable=SC1091
source .venv/bin/activate
sortie doctor
echo "starting API on :8787 …"
sortie api &
API_PID=$!
cleanup() { kill "$API_PID" 2>/dev/null || true; }
trap cleanup EXIT

for _ in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8787/api/health >/dev/null; then
    break
  fi
  sleep 0.3
done

cd apps/web
if [[ ! -d node_modules ]]; then
  npm install
fi
echo "starting workbench on :5173 …"
npm run dev
