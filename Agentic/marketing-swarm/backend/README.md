# Marketing Swarm Backend API

## Overview
FastAPI backend for the Marketing Swarm multi-agent AI system. This backend provides REST API endpoints and WebSocket support for real-time agent communication.

## Architecture
- **Framework**: FastAPI with Socket.IO
- **Database**: SQLite (local) / Cloud SQL (production)
- **Python Version**: 3.13+ compatible
- **Port**: 8001

## Quick Start

### Prerequisites
- Python 3.11+ (3.13+ uses simplified implementation)
- Virtual environment recommended

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database_simple.py
```

### Running the Server
```bash
# For Python 3.13+
python main_simple.py

# For Python < 3.13 (with CrewAI)
python main.py
```

The server will start on http://localhost:8001

## API Endpoints

### Health & Status
- `GET /api/health` - System health check
- `GET /api/agents/status` - Agent status check
- `GET /api/launch-status` - Launch progression status

### Conversation Management
- `POST /api/conversation/start` - Start a new conversation
  ```json
  {
    "user_query": "How should we launch our robo-advisor?",
    "test_mode": false
  }
  ```

### Emergency Controls
- `POST /api/emergency/demo-safe-mode` - Activate demo mode
- `POST /api/emergency/reset-system` - Reset the system

## WebSocket Events

### Client → Server
- `connect` - Initial connection
- `join_conversation` - Join a conversation room
- `start_conversation` - Start a new conversation via WebSocket

### Server → Client
- `connection_established` - Connection confirmed
- `agent_response` - Agent message
- `conversation_complete` - Conversation finished
- `conversation_error` - Error occurred

## Agent System

### Available Agents
1. **Sarah** - Brand Strategy Lead
2. **Marcus** - Digital Campaign Manager
3. **Elena** - Content Marketing Specialist
4. **David** - Customer Experience Designer
5. **Priya** - Marketing Analytics Manager
6. **Alex** - Growth Marketing Lead

### Agent Response Flow
1. **Phase 1: Analysis** (45-60 seconds)
   - Initial query analysis
   - Web search simulation
   - Domain expertise application

2. **Phase 2: Collaboration** (90-120 seconds)
   - Inter-agent discussion
   - Building on insights
   - Cross-functional perspectives

3. **Phase 3: Synthesis** (60-90 seconds)
   - Final recommendations
   - Action items
   - Strategic alignment

## Safety Systems

### Budget Guard
- Prevents excessive API usage
- Tracks daily spending
- Enforces per-session limits

### Compliance Filter
- Filters non-compliant financial advice
- Adds required disclaimers
- Prevents regulatory violations

### Input Sanitizer
- Limits input length
- Removes malicious patterns
- Protects against injection attacks

## Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    user_query TEXT NOT NULL,
    user_id TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata TEXT
);
```

### Agent Responses Table
```sql
CREATE TABLE agent_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT,
    agent_name TEXT NOT NULL,
    message TEXT NOT NULL,
    phase TEXT,
    has_web_data BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

## Configuration

### Environment Variables
Create a `.env` file:
```bash
OPENAI_API_KEY=your_key_here
FASTAPI_SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./test_marketing_swarm.db
ENVIRONMENT=development
```

### Settings
Configuration is managed in `utils/config.py`:
- API rate limits
- Timeout settings
- Agent parameters
- Safety thresholds

## Development

### Running Tests
```bash
pytest tests/
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Mock Mode
The system runs in mock mode by default (no real API calls):
- Simulated agent responses
- Predictable timing
- No API costs

## Deployment

### Local Development
```bash
python main_simple.py
```

### Production (Cloud Run)
```bash
# Build Docker image
docker build -t marketing-swarm-backend .

# Run with Cloud SQL
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql://user:pass@/dbname?host=/cloudsql/instance" \
  marketing-swarm-backend
```

## Monitoring

### Logs
- Location: `logs/system.log`
- Rotation: 500MB max, 10 days retention
- Level: Configurable via LOG_LEVEL env var

### Metrics
- Response times
- Agent performance
- Error rates
- API usage

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all `__init__.py` files exist
2. **Port conflicts**: Change port in main.py if 8001 is taken
3. **Database errors**: Run `init_database_simple.py` to initialize

### Emergency Procedures
- Demo safe mode: Activates pre-recorded responses
- System reset: Clears all active conversations
- Health checks: Verify all components are running

## API Examples

### Start a Conversation
```bash
curl -X POST http://localhost:8001/api/conversation/start \
  -H "Content-Type: application/json" \
  -d '{"user_query": "How to improve our CAC?"}'
```

### Check Agent Status
```bash
curl http://localhost:8001/api/agents/status | jq
```

### Monitor Health
```bash
watch -n 5 'curl -s http://localhost:8001/api/health | jq'
```