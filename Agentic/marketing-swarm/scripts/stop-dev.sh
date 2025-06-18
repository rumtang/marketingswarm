#!/bin/bash
# Stop development environment

echo "🛑 Stopping Marketing Swarm Development Environment..."

# Read PIDs if saved
if [ -f ".dev-pids" ]; then
    PIDS=$(cat .dev-pids)
    echo "Stopping processes: $PIDS"
    kill $PIDS 2>/dev/null
    rm .dev-pids
    echo "✅ Processes stopped"
else
    echo "⚠️  No .dev-pids file found"
    echo "Attempting to find and stop processes..."
    
    # Try to find and kill backend
    BACKEND_PID=$(lsof -ti:8000)
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID
        echo "✅ Backend stopped (PID: $BACKEND_PID)"
    fi
    
    # Try to find and kill frontend
    FRONTEND_PID=$(lsof -ti:3000)
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID
        echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    fi
fi

echo "✅ Development environment stopped"