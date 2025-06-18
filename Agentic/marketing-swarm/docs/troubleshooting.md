# Marketing Swarm Troubleshooting Guide

## 🔍 Common Issues and Solutions

### Backend Issues

#### 1. Python Version Compatibility
**Problem**: `ERROR: Could not find a version that satisfies the requirement crewai==0.41.1`

**Solution**:
```bash
# Check Python version
python --version

# If Python >= 3.13, use main_simple.py instead of main.py
cd backend
python main_simple.py
```

#### 2. Port Already in Use
**Problem**: `[Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use a different port
python main_simple.py --port 8002
```

#### 3. Database Connection Errors
**Problem**: `sqlite3.OperationalError: unable to open database file`

**Solution**:
```bash
# Initialize the database
cd backend
python scripts/init_database_simple.py

# Verify database exists
ls -la test_marketing_swarm.db
```

### Frontend Issues

#### 1. "Cannot read properties of undefined"
**Problem**: React components trying to access undefined data

**Solution**:
Add defensive checks in components:
```javascript
// Instead of:
{data.property}

// Use:
{data?.property || 'Loading...'}
```

#### 2. Proxy Error
**Problem**: `Proxy error: Could not proxy request /api/health from localhost:3001 to http://localhost:8001`

**Solution**:
1. Ensure backend is running on port 8001
2. Check `frontend/package.json` has `"proxy": "http://localhost:8001"`
3. Restart the frontend dev server

#### 3. WebSocket Connection Failed
**Problem**: Socket.IO not connecting to backend

**Solution**:
```javascript
// Check the connection URL in ConversationInterface.jsx
const socketUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Ensure backend is using socket_app, not app
uvicorn.run(socket_app, host="0.0.0.0", port=8001)
```

### WebSocket Issues

#### 1. CORS Errors
**Problem**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
Ensure backend CORS settings match frontend URL:
```python
sio = socketio.AsyncServer(
    cors_allowed_origins=["http://localhost:3001"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
)
```

#### 2. Connection Timeout
**Problem**: WebSocket connections timing out

**Solution**:
1. Check firewall settings
2. Verify WebSocket transport is enabled
3. Test with basic connection:
```javascript
const socket = io('http://localhost:8001');
socket.on('connect', () => console.log('Connected!'));
```

### Agent Issues

#### 1. Agents Not Responding
**Problem**: Agent responses are empty or undefined

**Solution**:
```bash
# Check agent status
curl http://localhost:8001/api/agents/status

# Verify all agents show "ready"
# If not, restart the backend
```

#### 2. Mock Responses Not Working
**Problem**: Agents return generic responses

**Solution**:
Ensure `main_simple.py` has the agent response logic implemented in the `SimpleAgentManager` class.

### Performance Issues

#### 1. Slow Response Times
**Problem**: Agent responses take too long

**Solution**:
- Reduce thinking time in test mode
- Check CPU/memory usage
- Use the performance monitoring endpoints

#### 2. Memory Leaks
**Problem**: Backend memory usage keeps growing

**Solution**:
- Restart the backend periodically
- Check for unclosed database connections
- Monitor with: `ps aux | grep python`

## 🚀 Quick Fixes

### Complete System Reset
```bash
# Stop all processes
pkill -f "python main"
pkill -f "npm start"

# Clear temporary files
rm -rf backend/__pycache__
rm -rf backend/logs/*

# Restart everything
cd backend && python main_simple.py &
cd frontend && npm start &
```

### Emergency Demo Mode
```bash
# Activate demo safe mode (uses pre-recorded responses)
curl -X POST http://localhost:8001/api/emergency/demo-safe-mode

# Reset system
curl -X POST http://localhost:8001/api/emergency/reset-system
```

### Health Check Commands
```bash
# Backend health
curl http://localhost:8001/api/health | jq

# Agent status
curl http://localhost:8001/api/agents/status | jq

# Launch status
curl http://localhost:8001/api/launch-status | jq
```

## 📞 Getting Help

If issues persist:
1. Check the logs: `tail -f backend/logs/system.log`
2. Review CLAUDE.md for implementation details
3. Check PROJECT_PLAN.md for recent updates
4. Run the verification script: `./scripts/verify.sh`

## 🔍 Debug Mode

Enable debug logging:
```python
# In main_simple.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Monitor WebSocket events:
```javascript
// In browser console
localStorage.debug = 'socket.io-client:*';
```