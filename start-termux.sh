#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Start server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Try to open browser (Termux and fallbacks)
if command -v am &> /dev/null; then
    am start -a android.intent.action.VIEW -d http://localhost:8000 &
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000 &
elif command -v open &> /dev/null; then
    open http://localhost:8000 &
fi

# Keep server running
wait $SERVER_PID
