# Marketing Swarm 🚀

A dynamic multi-agent AI collaboration system that simulates a marketing team discussing strategies, campaigns, and business solutions.

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd marketing-swarm

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_database_simple.py

# 3. Set up frontend
cd ../frontend
npm install

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys (optional for mock mode)

# 5. Start the system
# Terminal 1:
cd backend && python main_simple.py

# Terminal 2:
cd frontend && npm start
```

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete implementation guide and architecture
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Project status and roadmap
- **[Backend README](backend/README.md)** - API documentation
- **[Frontend README](frontend/README.md)** - UI component guide
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🤖 The Team

- **Sarah** - Brand Strategy Lead: Visionary idealist who champions brand positioning
- **Marcus** - Digital Campaign Manager: Data-driven optimizer who demands metrics
- **Elena** - Content Marketing Specialist: Creative rebel pushing boundaries
- **David** - Customer Experience Designer: User advocate prioritizing UX
- **Priya** - Marketing Analytics Manager: Skeptical scientist requiring proof
- **Alex** - Growth Marketing Lead: Risk-taking experimenter with bold ideas

## ✨ Key Features

- **Dynamic Conversations**: Agents interrupt, debate, and build on each other naturally
- **Personality-Driven**: Each agent has quantified traits (assertiveness, contrarianism, creativity)
- **Real-Time Updates**: WebSocket-based live conversation streaming
- **Professional Output**: Generates executive summaries, action items, and implementation plans
- **Relationship Tracking**: Agents form alliances and conflicts that evolve over time

## =� Key Safety Features

- API budget enforcement (prevents cost overruns)
- Financial compliance filtering (SEC/FINRA compliant)
- Input sanitization (security protection)
- Graceful degradation (demo fallback mode)
- Real-time health monitoring
- Emergency recovery procedures

## =' System Requirements

- Python 3.11+
- Node.js 18+
- Redis (optional, for caching)
- OpenAI API key with web search access

## =� Monitoring & Debugging

- **Development Console**: http://localhost:3000/dev-console
- **Health Check**: http://localhost:8000/api/health
- **System Status**: http://localhost:8000/api/launch-status

## =� Emergency Commands

```bash
# Check system health
npm run health-check

# Activate demo safe mode
npm run demo-safe-mode

# Reset system
npm run reset-demo

# View logs
npm run view-logs
```

## =� Pre-Launch Checklist

Run through the checklist in `claude.md` under "Pre-Launch Safety Checklist" before any demo or deployment.

## > Contributing

Please read `claude.md` for development guidelines and best practices.

## =� License

[Your License Here]

---

**For complete documentation, architecture details, and troubleshooting, see `claude.md`**