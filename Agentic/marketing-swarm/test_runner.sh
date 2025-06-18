#!/bin/bash
# Test runner script for Marketing Swarm

echo "🚀 Marketing Swarm Test Runner"
echo "=============================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}Please update backend/.env with your API keys before running tests${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to wait for server
wait_for_server() {
    echo "⏳ Waiting for backend to start..."
    for i in {1..30}; do
        curl -s http://localhost:8000/api/health > /dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Backend is ready${NC}"
            return 0
        fi
        sleep 1
    done
    echo -e "${RED}❌ Backend failed to start within 30 seconds${NC}"
    return 1
}

# Function to run tests
run_tests() {
    echo ""
    echo "🧪 Running tests..."
    echo ""
    
    # Run basic tests first
    echo "1️⃣ Running basic backend tests..."
    cd backend
    python test_basic.py
    BASIC_RESULT=$?
    cd ..
    
    if [ $BASIC_RESULT -ne 0 ]; then
        echo -e "${RED}❌ Basic tests failed${NC}"
        return 1
    fi
    
    # Run integration tests
    echo ""
    echo "2️⃣ Running integration tests..."
    cd backend
    python test_integration.py
    INTEGRATION_RESULT=$?
    cd ..
    
    return $INTEGRATION_RESULT
}

# Main execution
echo ""
echo "📋 Test Plan:"
echo "1. Check environment setup"
echo "2. Start backend server"
echo "3. Run basic tests"
echo "4. Run integration tests"
echo "5. Generate test report"
echo ""

# Check if backend is already running
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use${NC}"
    echo "Do you want to use the existing server? (y/n)"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please stop the existing server and run this script again"
        exit 1
    fi
    
    # Run tests with existing server
    run_tests
    TEST_RESULT=$?
else
    # Start backend server
    echo "🚀 Starting backend server..."
    cd backend
    python main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo "Backend PID: $BACKEND_PID"
    
    # Wait for server to be ready
    if wait_for_server; then
        # Run tests
        run_tests
        TEST_RESULT=$?
        
        # Stop backend
        echo ""
        echo "🛑 Stopping backend server..."
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
    else
        TEST_RESULT=1
        kill $BACKEND_PID 2>/dev/null
    fi
fi

# Generate test report
echo ""
echo "📊 Test Report"
echo "============="
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start the frontend: cd frontend && npm start"
    echo "2. Open http://localhost:3000"
    echo "3. Try the demo scenarios"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check backend.log for errors"
    echo "2. Verify .env configuration"
    echo "3. Ensure all dependencies are installed"
fi

exit $TEST_RESULT