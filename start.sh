#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "No .venv found — run ./setup.sh first."
  exit 1
fi

source .venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
