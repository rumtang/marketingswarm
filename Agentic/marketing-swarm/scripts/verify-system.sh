#!/bin/bash
# Marketing Swarm System Verification Script

echo "🧪 Marketing Swarm System Verification"
echo "====================================="

# Check if backend is running
echo -n "Checking backend API... "
HEALTH=$(curl -s http://localhost:8001/api/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Running"
    echo "  Response: $HEALTH"
else
    echo "❌ Not responding"
    echo "  Start with: cd backend && python main_simple.py"
    exit 1
fi

# Check agent status
echo -n "Checking agents... "
AGENTS=$(curl -s http://localhost:8001/api/agents/status 2>/dev/null | jq 'length' 2>/dev/null)
if [ "$AGENTS" == "6" ]; then
    echo "✅ All 6 agents ready"
else
    echo "⚠️  Only $AGENTS agents ready"
fi

# Check launch status
echo -n "Checking launch status... "
READY=$(curl -s http://localhost:8001/api/launch-status 2>/dev/null | jq -r '.ready_for_demo' 2>/dev/null)
if [ "$READY" == "true" ]; then
    echo "✅ System ready for demo"
else
    echo "⚠️  System not fully ready"
fi

# Check frontend
echo -n "Checking frontend... "
curl -s http://localhost:3001 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Running on port 3001"
else
    echo "❌ Not responding"
    echo "  Start with: cd frontend && npm start"
fi

# Check database
echo -n "Checking database... "
if [ -f "backend/test_marketing_swarm.db" ]; then
    echo "✅ Database file exists"
else
    echo "❌ Database not found"
    echo "  Initialize with: cd backend && python scripts/init_database_simple.py"
fi

echo ""
echo "📊 Summary"
echo "=========="
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "API Docs: http://localhost:8001/docs"
echo ""
echo "🎯 Demo Scenarios Ready to Test!"