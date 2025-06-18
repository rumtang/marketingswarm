#!/bin/bash

echo "🚀 Starting Marketing Swarm..."
echo "================================"

# Function to cleanup on exit
cleanup() {
    echo -e "\n\n🛑 Shutting down..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Check if backend is already running on port 8001
if lsof -i :8001 > /dev/null 2>&1; then
    echo "⚠️  Port 8001 is already in use. Please stop the existing process first."
    echo "   You can use: lsof -ti :8001 | xargs kill"
    exit 1
fi

# Start backend
echo "📦 Starting backend on port 8001..."
cd backend
python main_simple.py &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        exit 1
    fi
done

echo ""
echo "✅ Marketing Swarm is running!"
echo "================================"
echo ""
echo "🔌 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo "🎨 Demo Interface: Open demo.html in your browser"
echo ""
echo "For React Frontend (optional):"
echo "  cd frontend && npm start"
echo "  Open http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Keep script running
wait $BACKEND_PID