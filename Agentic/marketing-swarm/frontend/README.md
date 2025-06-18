# Marketing Swarm Frontend

## Overview
React-based frontend for the Marketing Swarm multi-agent AI system. Features real-time agent conversations, system monitoring, and responsive design.

## Architecture
- **Framework**: React 18 with TypeScript support
- **Styling**: Tailwind CSS
- **Real-time**: Socket.IO client
- **State Management**: React hooks + Context
- **Port**: 3001

## Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3001

## Project Structure
```
src/
├── components/          # React components
│   ├── ConversationInterface.jsx   # Main chat interface
│   ├── AgentCard.jsx              # Individual agent display
│   ├── LiveFeed.jsx               # Real-time message feed
│   ├── SystemStatusDashboard.jsx   # System monitoring
│   └── TypingIndicator.jsx        # Loading animation
├── services/           # API and WebSocket services
│   └── api.js         # Backend API calls
├── hooks/             # Custom React hooks
├── utils/             # Utility functions
└── styles/            # CSS and styling

```

## Key Components

### ConversationInterface
Main component that handles:
- User query input
- WebSocket connection management
- Real-time message display
- Agent status tracking

```javascript
// Example usage
<ConversationInterface isDemoMode={false} />
```

### SystemStatusDashboard
Monitors system health:
- Backend API status
- WebSocket connectivity
- Agent availability
- Launch progression

```javascript
// Example usage
<SystemStatusDashboard 
  healthStatus={healthData}
  launchStatus={launchData}
/>
```

### AgentCard
Displays individual agent information:
- Agent name and role
- Active/thinking status
- Web data indicator

```javascript
// Example usage
<AgentCard 
  agent={{id: 'sarah', name: 'Sarah', role: 'Brand Strategy Lead'}}
  isActive={true}
  hasWebData={false}
/>
```

## WebSocket Integration

### Connection Setup
```javascript
const socketUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const socket = io(socketUrl, {
  transports: ['websocket'],
});
```

### Event Handlers
- `connect` - Connection established
- `agent_response` - New agent message
- `conversation_complete` - Conversation finished
- `conversation_error` - Error occurred

## API Integration

### Services
All API calls are centralized in `services/api.js`:

```javascript
// Start a conversation
const response = await startConversation(query, testMode);

// Check system health
const health = await getHealth();

// Get agent status
const agents = await getAgentStatus();
```

## Styling

### Tailwind CSS
The project uses Tailwind for styling:
- Responsive design
- Dark mode support
- Custom color scheme
- Animation utilities

### Color Scheme
- Primary: Blue (`primary-600`)
- Success: Green (`green-500`)
- Warning: Yellow (`yellow-500`)
- Error: Red (`red-500`)

## State Management

### Component State
- `useState` for local state
- `useEffect` for side effects
- `useRef` for DOM references
- `useContext` for global state (if needed)

### WebSocket State
Managed in ConversationInterface:
- Connection status
- Message history
- Active agents
- Loading states

## Error Handling

### Error Boundaries
Wrap components to catch errors:
```javascript
<ErrorBoundary>
  <ConversationInterface />
</ErrorBoundary>
```

### Defensive Rendering
Always check for data existence:
```javascript
{data?.property && (
  <div>{data.property}</div>
)}
```

## Environment Variables

Create `.env` file:
```bash
REACT_APP_API_URL=http://localhost:8001
```

## Development

### Available Scripts
- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run eject` - Eject from Create React App

### Hot Reloading
Development server includes:
- Auto-refresh on file changes
- Error overlay
- Fast refresh for React components

### Debugging
1. Use React Developer Tools
2. Enable Socket.IO debugging:
   ```javascript
   localStorage.debug = 'socket.io-client:*';
   ```
3. Check Network tab for API calls

## Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
Test WebSocket connections:
```javascript
window.connectionTester.runAllTests()
```

## Build & Deployment

### Production Build
```bash
npm run build
```

Creates optimized build in `build/` directory.

### Deployment Options
1. **Vercel**: `vercel deploy`
2. **Netlify**: Drag & drop build folder
3. **Docker**: Use provided Dockerfile
4. **Cloud Run**: Deploy with Cloud Build

## Common Issues

### Proxy Errors
Ensure `package.json` has:
```json
"proxy": "http://localhost:8001"
```

### WebSocket Connection Failed
1. Check backend is running on port 8001
2. Verify CORS settings
3. Test with direct connection

### Undefined Errors
Add defensive checks:
```javascript
// Before
{data.items.map(...)}

// After
{data?.items?.map(...) || []}
```

## Performance Optimization

### Code Splitting
React automatically splits code by route.

### Lazy Loading
```javascript
const SystemStatus = React.lazy(() => import('./SystemStatusDashboard'));
```

### Memoization
```javascript
const MemoizedAgent = React.memo(AgentCard);
```

## Accessibility

### ARIA Labels
All interactive elements have proper labels.

### Keyboard Navigation
- Tab through all controls
- Enter to submit
- Escape to close modals

### Screen Reader Support
- Semantic HTML
- Role attributes
- Live regions for updates

## Future Enhancements
1. Add dark mode toggle
2. Implement conversation history
3. Add export functionality
4. Enhanced animations
5. Mobile app version