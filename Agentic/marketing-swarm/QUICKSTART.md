# Marketing Swarm - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required: OPENAI_API_KEY=sk-your-key-here
# Required: FASTAPI_SECRET_KEY=your-secret-key-here
```

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend
python main.py
```

The backend will start on http://localhost:8000

### 4. Frontend Setup (new terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

The frontend will start on http://localhost:3000

## 🧪 Testing the System

### Quick Health Check
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Check agent status
curl http://localhost:8000/api/agents/status

# Check launch readiness
curl http://localhost:8000/api/launch-status
```

### Test a Conversation
1. Open http://localhost:3000
2. Enter a test query like: "How should we launch our new robo-advisor?"
3. Watch the agents collaborate in real-time

### Using the Dev Console
1. Click "Dev Console" in the header
2. Monitor system health, connections, and logs
3. Use quick action buttons to test various functions

## 🛠️ Troubleshooting

### Backend Won't Start
- Check Python version: `python --version` (needs 3.11+)
- Verify .env file exists and has required keys
- Check port 8000 is free: `lsof -i :8000`

### Frontend Won't Start  
- Check Node version: `node --version` (needs 18+)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Agents Not Responding
- Verify OpenAI API key is valid
- Check budget limits in .env (DAILY_API_BUDGET)
- Try demo safe mode: `curl -X POST http://localhost:8000/api/emergency/demo-safe-mode`

### WebSocket Connection Issues
- Check browser console for errors
- Ensure both backend and frontend are running
- Try a different browser

## 📊 Monitoring

- **System Status**: http://localhost:3000 → Click "System Status"
- **API Docs**: http://localhost:8000/docs
- **Logs**: Check `backend/logs/system.log`

## 🚨 Emergency Commands

```bash
# Reset the system
curl -X POST http://localhost:8000/api/emergency/reset-system

# Activate demo safe mode (no API calls)
curl -X POST http://localhost:8000/api/emergency/demo-safe-mode

# Check all connections
cd frontend && npm run test-connections
```

## 💡 Demo Scenarios

Try these queries to see different agent interactions:

1. **Product Launch**: "How should we launch our new robo-advisor to compete with Betterment?"
2. **Cost Optimization**: "Our customer acquisition cost has doubled. What's our action plan?"
3. **Compliance**: "How do we market complex derivatives to retail investors compliantly?"
4. **Demographics**: "We need a content strategy that builds trust with Gen Z about retirement planning."
5. **Conversion**: "Our mobile app conversion rate is 2%. Industry average is 8%. Help."

## 🔗 Next Steps

- Read the full documentation in `claude.md`
- Explore the codebase structure
- Customize agent personalities and behaviors
- Add your own demo scenarios

---

**Need help?** Check `claude.md` for comprehensive documentation and troubleshooting.