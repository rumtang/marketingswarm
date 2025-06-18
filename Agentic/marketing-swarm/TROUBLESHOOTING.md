# Marketing Swarm - Troubleshooting Guide

## 🔧 Frontend-Backend Connection Issues SOLVED

### Problem: Frontend not connecting to backend

The issue was a **Socket.IO vs WebSocket incompatibility**. The frontend uses Socket.IO client, but some backend implementations were using raw WebSocket, which are not compatible protocols.

### Solution Applied

1. **Modified `main_simple.py`** to use Socket.IO instead of raw WebSocket
2. **Added proper Socket.IO event handlers** matching what the frontend expects:
   - `connect` event
   - `join_conversation` event  
   - `agent_response` event
   - `conversation_complete` event
   - `conversation_error` event

3. **Ensured both run on correct ports**:
   - Backend: Port 8001
   - Frontend: Port 3001

## 🚀 Quick Start Guide

### Option 1: Using the Simplified Backend (Recommended)

```bash
# Terminal 1 - Start Backend
cd backend
python main_simple.py

# Terminal 2 - Start Frontend
cd frontend
npm start
```

### Option 2: Using the Helper Script

```bash
# Use the startup helper
python start_backend.py
# Choose option 1 for main_simple.py

# In another terminal
cd frontend
npm start
```

### Option 3: Testing with Socket.IO

```bash
# Test the Socket.IO connection
python test_socketio.py
```

## 📋 Connection Checklist

### Backend Health Check
```bash
curl http://localhost:8001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-17T...",
  "version": "1.0.0",
  "mode": "simple"
}
```

### Frontend Connection Test
1. Open browser developer console (F12)
2. Look for console message: "Connected to backend"
3. Check Network tab for Socket.IO connection (should show status 101)

## 🐛 Common Issues and Fixes

### Issue: "WebSocket connection failed"
**Cause**: Using incompatible WebSocket instead of Socket.IO
**Fix**: Use `main_simple.py` or `main.py` (both have Socket.IO support)

### Issue: "CORS errors in browser"
**Cause**: Frontend and backend on different ports without proper CORS
**Fix**: Already configured in both backend files for ports 3000 and 3001

### Issue: "Cannot connect to backend"
**Cause**: Backend not running or on wrong port
**Fix**: 
1. Ensure backend is running on port 8001
2. Check frontend is configured to connect to port 8001
3. Verify no firewall blocking localhost connections

### Issue: "Agent responses not appearing"
**Cause**: Socket.IO events not properly configured
**Fix**: The modified `main_simple.py` now sends correct event format

## 🔍 Debugging Steps

1. **Check Backend Logs**
   ```bash
   # You should see:
   # "Client connected: <socket-id>"
   # "Starting conversation..."
   ```

2. **Check Frontend Console**
   ```javascript
   // In browser console, you should see:
   // "Connected to backend"
   // Socket.IO event logs
   ```

3. **Test Individual Components**
   ```bash
   # Test API endpoints
   curl http://localhost:8001/api/agents/status
   
   # Test Socket.IO connection
   python test_socketio.py
   ```

## 📁 File Structure Explanation

- **`main.py`**: Full-featured backend with complete agent system (port 8001)
- **`main_simple.py`**: Simplified backend with Socket.IO support (port 8001) ✅ RECOMMENDED
- **`minimal_server.py`**: Basic WebSocket demo (port 8000) - NOT compatible with React frontend
- **`demo.html`**: Standalone demo that works with WebSocket backends
- **`test_socketio.py`**: Socket.IO connection tester
- **`start_backend.py`**: Helper script to choose which backend to run

## 🎯 Next Steps

1. **Start Development**:
   ```bash
   cd backend && python main_simple.py
   cd frontend && npm start
   ```

2. **Access the Application**:
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

3. **Test a Conversation**:
   - Click one of the example queries
   - Or type your own marketing question
   - Watch the agents collaborate in real-time

## 💡 Pro Tips

- Use `main_simple.py` for development - it's simpler and has fewer dependencies
- The frontend automatically reconnects if the backend restarts
- Check the browser Network tab to see Socket.IO frames for debugging
- Use the demo.html file for a quick standalone test without React

## 🆘 Still Having Issues?

1. **Restart Everything**:
   ```bash
   # Kill all Python processes
   pkill -f python
   
   # Kill all Node processes  
   pkill -f node
   
   # Start fresh
   ```

2. **Check Dependencies**:
   ```bash
   cd backend
   pip install python-socketio fastapi uvicorn
   
   cd ../frontend
   npm install socket.io-client
   ```

3. **Verify Ports Are Free**:
   ```bash
   lsof -i :8001  # Should be empty before starting
   lsof -i :3001  # Should be empty before starting
   ```

The connection issues have been resolved by ensuring Socket.IO compatibility between frontend and backend!