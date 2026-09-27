#!/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Gram Vaani (RuralAI)"
echo "==============================="
echo ""

cleanup() {
	if [[ -n "${BACKEND_PID:-}" ]]; then
		kill "$BACKEND_PID" 2>/dev/null || true
	fi
	if [[ -n "${FRONTEND_PID:-}" ]]; then
		kill "$FRONTEND_PID" 2>/dev/null || true
	fi
}

trap cleanup INT TERM EXIT

# Start backend
echo "Starting Backend on http://localhost:8000..."
cd "$ROOT_DIR/backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Frontend on http://localhost:5173..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Both servers started."
echo ""
echo "Access URLs:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

wait
