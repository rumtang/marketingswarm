#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo "🔍 Marketing Swarm System Monitor"
echo "================================="
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    # Clear previous output
    tput cup 4 0
    
    # Get current time
    echo -e "${YELLOW}Last Update: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
    
    # Backend Health
    echo -e "${YELLOW}Backend Health:${NC}"
    HEALTH=$(curl -s http://localhost:8001/api/health 2>/dev/null)
    if [ $? -eq 0 ]; then
        STATUS=$(echo $HEALTH | jq -r '.status' 2>/dev/null || echo "error")
        MODE=$(echo $HEALTH | jq -r '.mode' 2>/dev/null || echo "unknown")
        if [ "$STATUS" = "healthy" ]; then
            echo -e "  Status: ${GREEN}✅ $STATUS${NC}"
        else
            echo -e "  Status: ${RED}❌ $STATUS${NC}"
        fi
        echo -e "  Mode: $MODE"
    else
        echo -e "  Status: ${RED}❌ Not responding${NC}"
    fi
    echo ""
    
    # Agent Status
    echo -e "${YELLOW}Agent Status:${NC}"
    AGENTS=$(curl -s http://localhost:8001/api/agents/status 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "$AGENTS" | jq -r 'to_entries[] | "  \(.key): \(.value.status)"' | while read line; do
            if [[ $line == *"ready"* ]]; then
                echo -e "${GREEN}✅${NC} $line"
            else
                echo -e "${RED}❌${NC} $line"
            fi
        done
    else
        echo -e "  ${RED}❌ Unable to fetch agent status${NC}"
    fi
    echo ""
    
    # Launch Status
    echo -e "${YELLOW}Launch Status:${NC}"
    LAUNCH=$(curl -s http://localhost:8001/api/launch-status 2>/dev/null)
    if [ $? -eq 0 ]; then
        PROGRESS=$(echo $LAUNCH | jq -r '.overall_progress' 2>/dev/null || echo "unknown")
        PERCENTAGE=$(echo $LAUNCH | jq -r '.percentage' 2>/dev/null || echo "0")
        READY=$(echo $LAUNCH | jq -r '.ready_for_demo' 2>/dev/null || echo "false")
        
        echo -e "  Progress: $PROGRESS ($PERCENTAGE%)"
        if [ "$READY" = "true" ]; then
            echo -e "  Demo Ready: ${GREEN}✅ Yes${NC}"
        else
            echo -e "  Demo Ready: ${RED}❌ No${NC}"
        fi
    else
        echo -e "  ${RED}❌ Unable to fetch launch status${NC}"
    fi
    echo ""
    
    # Active Processes
    echo -e "${YELLOW}Active Processes:${NC}"
    BACKEND_PID=$(pgrep -f "main_simple.py" | head -1)
    FRONTEND_PID=$(pgrep -f "react-scripts start" | head -1)
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "  Backend: ${GREEN}✅ Running (PID: $BACKEND_PID)${NC}"
    else
        echo -e "  Backend: ${RED}❌ Not running${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "  Frontend: ${GREEN}✅ Running (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "  Frontend: ${RED}❌ Not running${NC}"
    fi
    echo ""
    
    # URLs
    echo -e "${YELLOW}Access URLs:${NC}"
    echo "  Frontend: http://localhost:3001"
    echo "  Backend API: http://localhost:8001"
    echo "  API Docs: http://localhost:8001/docs"
    echo ""
    
    # Refresh every 5 seconds
    sleep 5
done