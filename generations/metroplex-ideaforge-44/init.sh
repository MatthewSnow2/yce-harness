#!/bin/bash
set -e

echo "=== VoiceAgent QA Platform Setup ==="

# Backend setup
if [ ! -d "backend" ]; then
    echo "Backend directory not found. Skipping backend setup."
else
    echo "Setting up backend..."
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found yet"
    cd ..
fi

# Frontend setup
if [ ! -d "frontend" ]; then
    echo "Frontend directory not found. Skipping frontend setup."
else
    echo "Setting up frontend..."
    cd frontend
    npm install 2>/dev/null || echo "No package.json found yet"
    cd ..
fi

# Start services
echo "Starting services..."
if [ -d "backend" ] && [ -f "backend/app/main.py" ]; then
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo "Backend started on http://localhost:8000 (PID: $BACKEND_PID)"
fi

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started on http://localhost:5173 (PID: $FRONTEND_PID)"
fi

echo "=== Setup Complete ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"

wait
