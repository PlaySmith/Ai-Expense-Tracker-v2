#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting ET V2 - Backend & Frontend..."
echo "Project path: $SCRIPT_DIR"

# Backend (bg)
cd "$SCRIPT_DIR/backend"
echo "Installing backend deps..."
pip install -r requirements.txt -q &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Frontend (bg) - in separate terminal or foreground
(cd "$SCRIPT_DIR/frontend" && echo "Installing frontend deps..." && npm install && npm run dev) &

echo ""
echo "==================== 🚀 ET V2 RUNNING ===================="
echo "Backend:  http://localhost:8000/docs  (Swagger API)"
echo "Frontend: http://localhost:3001       (React UI)"
echo "=========================================================="
echo "Stop: Ctrl+C or kill processes"
echo ""

wait

