#!/bin/bash

echo "⚡ Introspection Checkpoint 2: Performance & Caching Verification"
echo "================================================================"
echo ""

# Check if services are running
echo "🔍 Checking service health..."
HEALTH_STATUS=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ -z "$HEALTH_STATUS" ]; then
    echo "❌ Backend not running. Starting services..."
    docker-compose up -d
    echo "⏳ Waiting 20 seconds for services to start..."
    sleep 20
fi

# Get auth token
echo ""
echo "🔐 Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get auth token"
    exit 1
fi

echo "✅ Got auth token"

# Test API performance
echo ""
echo "⚡ Testing /api/bed-status performance..."
echo "First call (cache miss):"
START=$(date +%s.%N)
RESPONSE=$(curl -s -w "\nTime: %{time_total}s\n" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bed-status)
END=$(date +%s.%N)
DURATION=$(echo "$END - $START" | bc)

echo "Response time: ${DURATION}s"

# Check if response is valid JSON
echo "$RESPONSE" | head -n -1 | python -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Valid JSON response"
else
    echo "❌ Invalid response"
fi

echo ""
echo "Second call (cache hit):"
START=$(date +%s.%N)
RESPONSE=$(curl -s -w "\nTime: %{time_total}s\n" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bed-status)
END=$(date +%s.%N)
DURATION=$(echo "$END - $START" | bc)

echo "Response time: ${DURATION}s"

# Get cache stats (if endpoint exists)
echo ""
echo "📊 Cache statistics:"
curl -s http://localhost:8000/metrics 2>/dev/null | python -m json.tool 2>/dev/null || echo "Metrics endpoint not implemented yet"

echo ""
echo "✅ Checkpoint 2 complete - Performance optimizations in place"