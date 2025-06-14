#!/bin/bash

# PCC Prototype Launch Script
# This script provides a clean, reliable launch of the system

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 PCC Prototype Launch Sequence"
echo "================================"
echo ""

# Check Docker
echo "🔍 Checking Docker..."
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Check .env file
echo ""
echo "🔍 Checking environment..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please edit .env and add your OPENAI_API_KEY${NC}"
    exit 1
fi

# Check if OPENAI_API_KEY is set in .env
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${RED}❌ OPENAI_API_KEY not set in .env file${NC}"
    echo "Please edit .env and add your OpenAI API key"
    exit 1
fi
echo -e "${GREEN}✅ Environment configured${NC}"

# Clean previous state
echo ""
echo "🧹 Cleaning previous state..."
docker-compose down -v >/dev/null 2>&1 || true
echo -e "${GREEN}✅ Clean slate ready${NC}"

# Build and start services
echo ""
echo "🏗️  Building and starting services..."
echo "This may take 2-3 minutes on first run..."
docker-compose up --build -d

# Wait for services
echo ""
echo "⏳ Waiting for services to initialize..."
for i in {1..30}; do
    printf "."
    sleep 1
done
echo ""

# Check health
echo ""
echo "🏥 Checking system health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null || echo "{}")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may still be starting up${NC}"
    echo "Check manually: curl http://localhost:8000/health"
fi

# Final instructions
echo ""
echo "🎉 Launch Complete!"
echo ""
echo "📍 Access Points:"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health:   http://localhost:8000/health"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop system:  docker-compose down"
echo "   Restart:      docker-compose restart backend"
echo ""

# Try to open browser
if command -v open >/dev/null 2>&1; then
    echo "🌐 Opening browser..."
    sleep 2
    open http://localhost:5173
elif command -v xdg-open >/dev/null 2>&1; then
    echo "🌐 Opening browser..."
    sleep 2
    xdg-open http://localhost:5173
fi

echo -e "${GREEN}✨ System is ready for demo!${NC}"