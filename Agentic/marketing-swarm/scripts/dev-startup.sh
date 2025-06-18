#!/bin/bash
# Bulletproof development startup script

echo "=€ Starting Marketing Swarm Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN} $1${NC}"
    else
        echo -e "${RED}L $1${NC}"
        exit 1
    fi
}

# Step 1: Environment validation
echo -e "\n${YELLOW}=Ë Step 1: Validating environment...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}L .env file missing. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}   Please update .env with your API keys before continuing${NC}"
    exit 1
fi

# Source environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required environment variables
required_vars=("OPENAI_API_KEY" "FASTAPI_SECRET_KEY" "DATABASE_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}L Required environment variable $var not set${NC}"
        exit 1
    fi
done
check_status "Environment validation passed"

# Step 2: Backend setup
echo -e "\n${YELLOW}=Ë Step 2: Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    check_status "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
check_status "Virtual environment activated"

# Install/update dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
check_status "Backend dependencies installed"

# Run startup health checks
echo "Running backend health checks..."
python -c "
import sys
sys.path.append('.')
from utils.config import validate_environment
if not validate_environment():
    sys.exit(1)
print('Backend configuration validated')
"
check_status "Backend health checks passed"

# Start backend in background
echo "Starting backend server..."
python main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo -e "${YELLOW}ó Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null; then
        check_status "Backend is ready"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}L Backend failed to start within 30 seconds${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
done

# Step 3: Frontend setup
echo -e "\n${YELLOW}=Ë Step 3: Setting up frontend...${NC}"
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
    check_status "Frontend dependencies installed"
fi

# Start frontend
echo "Starting frontend..."
npm start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
echo -e "${YELLOW}ó Waiting for frontend to be ready...${NC}"
sleep 10
curl -s http://localhost:3000 > /dev/null
check_status "Frontend is accessible"

# Step 4: Run integration tests
echo -e "\n${YELLOW}=Ë Step 4: Running integration tests...${NC}"
cd ..

# Create simple test script
cat > test_integration.js << 'EOF'
const axios = require('axios');

async function runTests() {
    try {
        // Test backend health
        const health = await axios.get('http://localhost:8000/api/health');
        console.log(' Backend health check passed');
        
        // Test agent status
        const agents = await axios.get('http://localhost:8000/api/agents/status');
        console.log(' Agent status check passed');
        
        // Test launch status
        const launch = await axios.get('http://localhost:8000/api/launch-status');
        console.log(` Launch status: ${launch.data.percentage}% ready`);
        
        return true;
    } catch (error) {
        console.error('L Integration test failed:', error.message);
        return false;
    }
}

runTests().then(success => {
    process.exit(success ? 0 : 1);
});
EOF

node test_integration.js
check_status "Integration tests passed"

# Clean up test file
rm test_integration.js

# Save PIDs for easy cleanup
echo "$BACKEND_PID $FRONTEND_PID" > .dev-pids

# Final output
echo -e "\n${GREEN}<‰ Development environment ready!${NC}"
echo -e "=Ê Open http://localhost:3000 for the main interface"
echo -e "=à  Open http://localhost:3000 (then click Dev Console) for development dashboard"
echo -e "=Ú API documentation: http://localhost:8000/docs"
echo -e "\n${YELLOW}To stop the environment:${NC}"
echo -e "   kill $BACKEND_PID $FRONTEND_PID"
echo -e "   OR"
echo -e "   ./scripts/stop-dev.sh"

# Keep script running
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"
wait