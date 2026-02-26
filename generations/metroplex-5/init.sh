#!/bin/bash
set -e

echo "Starting AI Agent Analytics Platform..."

# Install backend dependencies
echo "Setting up backend..."
cd "$(dirname "$0")/backend"
if [ ! -d ".venv" ]; then
    uv venv
fi
source .venv/bin/activate
uv pip install -r requirements.txt

# Start backend server in background
echo "Starting backend server on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Install frontend dependencies
echo "Setting up frontend..."
cd "$(dirname "$0")/frontend"
bun install

# Start frontend dev server
echo "Starting frontend on port 3000..."
bun run dev &
FRONTEND_PID=$!

echo ""
echo "Application is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
