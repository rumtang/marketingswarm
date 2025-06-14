# 🚀 PCC Prototype Launch Guide

## Quick Launch (5 minutes)

### 1. Prerequisites Check
```bash
# Ensure Docker is running
docker --version

# Check environment variables
cat .env.example  # Use this as template for .env
```

### 2. Launch Services
```bash
# Clean start (recommended)
docker-compose down -v
docker-compose up --build -d

# Wait for services to be ready (20-30 seconds)
sleep 30
```

### 3. Verify Health
```bash
# Check all services are running
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Launch Checklist

### Pre-Launch
- [ ] Docker Desktop running
- [ ] `.env` file created with OPENAI_API_KEY
- [ ] Port 5173 (frontend) available
- [ ] Port 8000 (backend) available
- [ ] Port 9092 (Kafka) available
- [ ] At least 4GB RAM available for Docker

### Launch Steps
- [ ] Run `docker-compose down -v` to clean previous state
- [ ] Run `docker-compose up --build -d` to start fresh
- [ ] Wait 30 seconds for services to initialize
- [ ] Verify health endpoint returns "healthy"
- [ ] Open frontend at http://localhost:5173
- [ ] Login with demo credentials

### Post-Launch Verification
- [ ] Dashboard loads without errors
- [ ] Real-time updates appear (bed status changes)
- [ ] WebSocket connection established (check browser console)
- [ ] No errors in browser console
- [ ] API response times <1 second

## 🔐 Demo Credentials

### Admin User
- Username: `admin`
- Password: `admin123`
- Role: Full system access

### Nurse User
- Username: `nurse`
- Password: `nurse123`
- Role: Clinical access

## 🎮 Demo Script

### 1. Initial Dashboard View
- Show real-time bed occupancy across units
- Highlight AI-generated patient narratives
- Point out emotional states and discharge barriers

### 2. Capacity Predictions
- Navigate to capacity forecast
- Show AI predictions based on narrative context
- Demonstrate how system considers hospital challenges

### 3. Discharge Acceleration
- Click on a patient with barriers
- Show AI-identified discharge barriers
- Demonstrate narrative-aware recommendations

### 4. Concierge Chat (if implemented)
- Open chat interface
- Ask about specific patients
- Show context-aware responses

### 5. Real-Time Updates
- Watch for automatic narrative events
- Show WebSocket-delivered updates
- Highlight AI insights as they appear

## 🛠️ Troubleshooting

### Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing OPENAI_API_KEY in .env
# - Port 8000 already in use
# - Insufficient memory
```

### Frontend Connection Issues
```bash
# Check frontend logs
docker-compose logs frontend

# Verify backend is accessible
curl http://localhost:8000/health
```

### Performance Issues
```bash
# Check cache statistics (if metrics endpoint exists)
curl http://localhost:8000/metrics

# Monitor resource usage
docker stats
```

### Complete Restart
```bash
# Full cleanup and restart
docker-compose down -v
docker system prune -f
docker-compose up --build -d
```

## 📊 Performance Expectations

### Current Performance (v0.2.1-beta)
- **API Response Time**: ~18ms (cached), ~50ms (uncached)
- **WebSocket Latency**: <50ms
- **Patient Generation**: <2 seconds (with caching)
- **Cache Hit Rate**: >80% after 5 minutes
- **Memory Usage**: ~500MB per service

### Known Limitations
- Initial startup takes 20-30 seconds
- First patient loads may be slower (cache warming)
- Maximum ~100 concurrent WebSocket connections
- LLM rate limits may affect event generation speed

## 🎯 Success Criteria

### Technical Success
- [ ] All services healthy
- [ ] API endpoints responding <1 second
- [ ] No errors in logs
- [ ] WebSocket connections stable
- [ ] Cache working effectively

### Demo Success
- [ ] Narrative engine creating compelling stories
- [ ] AI insights appearing naturally
- [ ] Real-time updates smooth
- [ ] No visible errors or delays
- [ ] Positive user feedback

## 📱 Mobile Access

The frontend is responsive and can be accessed on mobile devices:
1. Find your computer's IP address
2. Access `http://[YOUR-IP]:5173` from mobile browser
3. Use same login credentials

## 🔄 Quick Commands

```bash
# Start
./launch.sh

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart backend only
docker-compose restart backend

# Clear all data and restart
docker-compose down -v && docker-compose up -d
```

## 🚨 Emergency Procedures

### If Demo Crashes
1. Stay calm, acknowledge the issue
2. Run: `docker-compose restart backend`
3. Refresh the browser
4. Continue demo (data persists)

### If API Timeouts Occur
1. Check cache is working: `docker-compose logs backend | grep cache`
2. Restart backend: `docker-compose restart backend`
3. Consider reducing concurrent users

### If No Data Appears
1. Check narrative engine: `docker-compose logs backend | grep narrative`
2. Verify OPENAI_API_KEY is set
3. Check Kafka is running: `docker-compose ps kafka`

---

**Ready to launch? Start with the Quick Launch section above!** 🚀