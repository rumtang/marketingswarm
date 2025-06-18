#!/bin/bash

echo "🚀 Relaunching Marketing Swarm Application..."
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Kill any existing processes
echo -e "${YELLOW}Step 1: Cleaning up existing processes...${NC}"

# Kill existing Python processes on port 8001
lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 8001" || echo "📌 Port 8001 was already free"

# Kill existing Node processes on port 3001
lsof -ti:3001 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 3001" || echo "📌 Port 3001 was already free"

# Kill any existing marketing swarm Python processes
ps aux | grep -E "main_simple.py|main.py" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null && echo "✅ Killed existing backend processes" || echo "📌 No backend processes to kill"

# Wait a moment for ports to be released
sleep 2

# Step 2: Check environment
echo -e "\n${YELLOW}Step 2: Checking environment...${NC}"

# Check if .env exists in frontend
if [ ! -f "frontend/.env" ]; then
    echo -e "${RED}❌ frontend/.env not found. Creating it...${NC}"
    echo "REACT_APP_API_URL=http://localhost:8001" > frontend/.env
    echo "PORT=3001" >> frontend/.env
    echo "✅ Created frontend/.env with correct settings"
else
    echo "✅ frontend/.env exists"
    # Verify it has the correct API URL
    if grep -q "REACT_APP_API_URL=http://localhost:8001" frontend/.env; then
        echo "✅ API URL correctly set to port 8001"
    else
        echo -e "${YELLOW}⚠️  Updating API URL to port 8001...${NC}"
        sed -i '' 's/REACT_APP_API_URL=.*/REACT_APP_API_URL=http:\/\/localhost:8001/' frontend/.env 2>/dev/null || \
        sed -i 's/REACT_APP_API_URL=.*/REACT_APP_API_URL=http:\/\/localhost:8001/' frontend/.env
    fi
fi

# Step 3: Start Backend
echo -e "\n${YELLOW}Step 3: Starting Backend on port 8001...${NC}"
cd backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
else
    echo "📌 No virtual environment found, using system Python"
fi

# Start backend in background
echo "Starting backend server with Socket.IO support..."
python main_simple.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo -n "Waiting for backend to start"
for i in {1..30}; do
    if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo -e "\n${GREEN}✅ Backend is running on port 8001${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "\n${RED}❌ Backend failed to start. Check backend.log for errors${NC}"
        exit 1
    fi
done

# Verify all agents are ready
echo "Checking agent status..."
AGENTS_STATUS=$(curl -s http://localhost:8001/api/agents/status)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All agents initialized successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Agent status check failed${NC}"
fi

# Step 4: Start Frontend
echo -e "\n${YELLOW}Step 4: Starting Frontend on port 3001...${NC}"
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
echo "Starting frontend server..."
PORT=3001 npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo -n "Waiting for frontend to start"
for i in {1..45}; do
    if curl -s http://localhost:3001 > /dev/null 2>&1; then
        echo -e "\n${GREEN}✅ Frontend is running on port 3001${NC}"
        break
    fi
    echo -n "."
    sleep 2
    if [ $i -eq 45 ]; then
        echo -e "\n${YELLOW}⚠️  Frontend is taking longer than expected to start${NC}"
    fi
done

# Step 5: Final Status Check
echo -e "\n${YELLOW}Step 5: Final Status Check${NC}"
echo "============================================"

# Check backend health
HEALTH=$(curl -s http://localhost:8001/api/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend API:${NC} Healthy on port 8001"
    echo "   Response: $HEALTH"
else
    echo -e "${RED}❌ Backend API:${NC} Not responding"
fi

# Check frontend
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend:${NC} Running on port 3001"
else
    echo -e "${YELLOW}⚠️  Frontend:${NC} Still starting up..."
fi

# Display access information
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}🎉 Marketing Swarm is launching!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "📱 Frontend URL: ${GREEN}http://localhost:3001${NC}"
echo -e "🔧 Backend API: ${GREEN}http://localhost:8001${NC}"
echo -e "📊 API Health: ${GREEN}http://localhost:8001/api/health${NC}"
echo -e "🤖 Agent Status: ${GREEN}http://localhost:8001/api/agents/status${NC}"
echo ""
echo -e "${YELLOW}Process IDs:${NC}"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}To stop the application:${NC}"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "Backend: tail -f backend.log"
echo "Frontend: tail -f frontend.log"
echo ""
echo -e "${GREEN}The frontend will open automatically in your browser.${NC}"
echo -e "${GREEN}If not, navigate to http://localhost:3001${NC}"

# Save PIDs for easy shutdown
echo "$BACKEND_PID $FRONTEND_PID" > .running_pids

# Open browser after a short delay
sleep 3
if command -v open &> /dev/null; then
    open http://localhost:3001
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3001
fi