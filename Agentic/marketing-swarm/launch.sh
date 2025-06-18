#!/bin/bash

echo "🚀 Marketing Swarm - Launching System"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down Marketing Swarm...${NC}"
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    
    # Note about frontend
    echo -e "${YELLOW}Note: Frontend may still be running on port 3001${NC}"
    echo "To stop it: lsof -ti :3001 | xargs kill"
    
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Check Python version
echo "🐍 Checking Python version..."
python --version

# Step 1: Start Backend
echo -e "\n${YELLOW}📦 Starting Backend on port 8001...${NC}"

cd backend

# Check if port 8001 is already in use
if lsof -i :8001 > /dev/null 2>&1; then
    echo -e "${RED}❌ Port 8001 is already in use${NC}"
    echo "Run: lsof -ti :8001 | xargs kill"
    exit 1
fi

# Start backend
python main_simple.py &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        exit 1
    fi
done

# Show backend endpoints
echo ""
echo -e "${GREEN}✅ Backend Running${NC}"
echo "📍 API: http://localhost:8001"
echo "📚 Docs: http://localhost:8001/docs"
echo "🔍 Health: http://localhost:8001/api/health"

# Step 2: Frontend Instructions
echo -e "\n${YELLOW}🎨 Frontend Status${NC}"

# Check if frontend is already running
if lsof -i :3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend already running on port 3001${NC}"
    echo "📍 Access: http://localhost:3001"
else
    echo -e "${YELLOW}Frontend not running. To start:${NC}"
    echo "1. Open a new terminal"
    echo "2. cd frontend"
    echo "3. npm start"
    echo ""
    echo "Or use the HTML demo:"
    echo "📍 Open demo.html in your browser"
fi

# Step 3: System Status
echo -e "\n${GREEN}🎉 Marketing Swarm Ready!${NC}"
echo "===================================="
echo ""
echo "🤖 6 AI Marketing Agents Available:"
echo "   👔 Sarah - Brand Strategy"
echo "   📱 Marcus - Digital Campaigns" 
echo "   ✍️ Elena - Content Marketing"
echo "   🎨 David - Customer Experience"
echo "   📊 Priya - Marketing Analytics"
echo "   🚀 Alex - Growth Marketing"
echo ""
echo "💡 Try these demo queries:"
echo '   - "How should we launch our new robo-advisor?"'
echo '   - "Our CAC has doubled. What should we do?"'
echo '   - "We need a Gen Z retirement content strategy"'
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the backend${NC}"
echo ""

# Keep script running
wait $BACKEND_PID