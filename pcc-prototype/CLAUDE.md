# Claude AI Assistant Guide for PCC Prototype

## Project Overview
This is the Patient Care Coordination (PCC) Prototype - a demonstration system showcasing AI-powered healthcare coordination capabilities through a narrative-driven architecture.

## Core Architecture Principles

### 1. Narrative-Driven Design
- **Single Source of Truth**: The narrative engine generates all UI states and patient data
- **Demo-First Strategy**: Focus on compelling demonstrations over production features
- **Storytelling**: Each patient scenario tells a complete story with realistic healthcare dynamics

### 2. WebSocket Communication
- All real-time updates flow through WebSocket connections
- Frontend subscribes to narrative events
- Backend publishes state changes as narrative updates
- Maintain connection health monitoring

## Development Guidelines

### When Working on the Narrative Engine
- All patient data originates from `backend/app/narrative/`
- Scenarios are defined in `scenarios.py`
- The engine drives all state changes - never bypass it
- Test scenarios should cover complete patient journeys

### Frontend Development
- React components in `frontend/src/components/`
- Use Tailwind CSS for styling (no Bootstrap)
- Components should be narrative-reactive, not data-driven
- Focus on visual storytelling and compelling UI

### Agent Development
- Agents in `backend/app/agents/` provide AI insights
- Each agent has a specific healthcare focus
- Agents should enhance the narrative, not drive it
- Keep agent responses concise and actionable

## Testing Approach
- Test complete patient scenarios end-to-end
- Verify narrative consistency across sessions
- Ensure WebSocket reliability under various conditions
- Focus on demo reliability over edge cases

## Common Tasks

### Adding a New Patient Scenario
1. Define the scenario in `backend/app/narrative/scenarios.py`
2. Create narrative prompts in `prompts.py`
3. Update the engine to handle new scenario types
4. Test the complete patient journey

### Enhancing UI Components
1. Components should react to narrative events
2. Maintain visual consistency with healthcare context
3. Prioritize clarity and immediate understanding
4. Test with multiple concurrent scenarios

### Debugging WebSocket Issues
1. Check connection status in browser console
2. Verify backend WebSocket handler is running
3. Look for connection drops in Docker logs
4. Test with the WebSocket debug tool in frontend

## Important Constraints
- **No Production Features**: This is a demonstration system
- **Narrative First**: All features must fit the storytelling model
- **Healthcare Context**: Maintain medical realism and accuracy
- **Performance**: Optimize for smooth demos, not scale

## Quick Commands
- `docker-compose up` - Start the full system
- `docker-compose logs -f backend` - Watch backend logs
- `docker-compose logs -f frontend` - Watch frontend logs
- `docker-compose down -v` - Clean shutdown with volume cleanup

## Key Files
- `backend/app/narrative/engine.py` - Core narrative engine
- `frontend/src/hooks/useWebSocket.js` - WebSocket client logic
- `backend/app/main.py` - FastAPI app and WebSocket handlers
- `docker-compose.yml` - Container orchestration

## Remember
This is a **demonstration prototype** designed to showcase the potential of AI in healthcare coordination. Focus on creating compelling, realistic scenarios that highlight the value of AI-assisted patient care coordination.