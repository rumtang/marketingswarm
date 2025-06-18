import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, SparklesIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import io from 'socket.io-client';

import AgentCard from './AgentCard';
import LiveFeed from './LiveFeed';
import TypingIndicator from './TypingIndicator';
import { startConversation } from '../services/api';

const ConversationInterface = ({ isDemoMode }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeAgent, setActiveAgent] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);
  const feedRef = useRef(null);

  // Example queries
  const exampleQueries = [
    "How should we launch our new robo-advisor to compete with Betterment?",
    "Our customer acquisition cost has doubled. What's our action plan?",
    "How do we market complex derivatives to retail investors compliantly?",
    "We need a content strategy that builds trust with Gen Z about retirement planning.",
  ];

  useEffect(() => {
    // Initialize socket connection with proper configuration
    const socketUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
    
    console.log('Initializing Socket.IO connection to:', socketUrl);
    
    socketRef.current = io(socketUrl, {
      transports: ['websocket', 'polling'], // Allow fallback to polling
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 20000,
    });

    // Debug: Log all events
    socketRef.current.onAny((eventName, ...args) => {
      console.log(`[Socket Event] ${eventName}:`, args);
    });

    socketRef.current.on('connect', () => {
      console.log('✅ Connected to backend with ID:', socketRef.current.id);
      setIsConnected(true);
      toast.success('Connected to Marketing Swarm');
    });

    socketRef.current.on('connect_error', (error) => {
      console.error('❌ Connection error:', error.message);
      setIsConnected(false);
      toast.error('Connection failed. Retrying...');
    });

    socketRef.current.on('disconnect', (reason) => {
      console.log('🔌 Disconnected:', reason);
      setIsConnected(false);
    });

    // Handle all connection-related events
    socketRef.current.on('connection_established', (data) => {
      console.log('Connection established:', data);
    });

    socketRef.current.on('joined_conversation', (data) => {
      console.log('Joined conversation:', data.conversation_id);
    });

    socketRef.current.on('conversation_started', (data) => {
      console.log('Conversation started:', data);
    });

    // Handle agent messages - try multiple event names
    const handleAgentMessage = (data) => {
      console.log('Agent message received:', data);
      
      // Ensure we have the required fields
      if (data && data.agent && data.message) {
        setMessages(prev => [...prev, {
          ...data,
          timestamp: data.timestamp || new Date().toISOString()
        }]);
        
        setActiveAgent(data.agent);
        setTimeout(() => setActiveAgent(null), 1000);
      }
    };

    // Listen for multiple possible event names
    socketRef.current.on('agent_response', handleAgentMessage);
    socketRef.current.on('agent_message', handleAgentMessage);
    socketRef.current.on('message', handleAgentMessage);

    socketRef.current.on('conversation_complete', (data) => {
      console.log('Conversation completed:', data);
      setIsLoading(false);
      const duration = data.duration || 'unknown';
      toast.success(`Conversation completed${typeof duration === 'number' ? ` in ${Math.round(duration)}s` : ''}`);
    });

    socketRef.current.on('conversation_error', (data) => {
      console.error('Conversation error:', data);
      setIsLoading(false);
      toast.error(`Error: ${data.error || 'Unknown error'}`);
    });

    socketRef.current.on('error', (data) => {
      console.error('Socket error:', data);
      setIsLoading(false);
      toast.error(data.message || 'An error occurred');
    });

    // Cleanup on unmount
    return () => {
      console.log('Cleaning up socket connection');
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    // Check connection first
    if (!isConnected) {
      toast.error('Not connected to server. Please wait...');
      return;
    }

    setIsLoading(true);
    setMessages([]);
    setConversationId(null);

    try {
      console.log('Starting conversation with query:', query);
      
      const response = await startConversation(query, isDemoMode);
      
      console.log('Start conversation response:', response);
      
      if (response.status === 'blocked') {
        toast.error('Query contains non-compliant content');
        setIsLoading(false);
        return;
      }

      setConversationId(response.conversation_id);
      
      // Join conversation room with the query
      console.log('Joining conversation room:', response.conversation_id);
      socketRef.current.emit('join_conversation', {
        conversation_id: response.conversation_id,
        query: query // Include the query
      });

      // Set a timeout in case we don't get responses
      const responseTimeout = setTimeout(() => {
        if (messages.length === 0) {
          console.error('Timeout: No messages received after 30 seconds');
          toast.error('No response from agents. Please try again.');
          setIsLoading(false);
        }
      }, 30000); // 30 second timeout

      // Clear timeout when we get the first message
      const clearTimeoutOnMessage = () => {
        clearTimeout(responseTimeout);
      };
      
      // Use 'once' to automatically remove listener after first message
      socketRef.current.once('agent_response', clearTimeoutOnMessage);
      socketRef.current.once('agent_message', clearTimeoutOnMessage);
      socketRef.current.once('message', clearTimeoutOnMessage);

      toast.success('Marketing team is analyzing your query...');
    } catch (error) {
      console.error('Failed to start conversation:', error);
      toast.error('Failed to start conversation: ' + (error.message || 'Unknown error'));
      setIsLoading(false);
    }
  };

  const agents = [
    { id: 'sarah', name: 'Sarah', role: 'Brand Strategy Lead', color: 'purple' },
    { id: 'marcus', name: 'Marcus', role: 'Digital Campaign Manager', color: 'blue' },
    { id: 'elena', name: 'Elena', role: 'Content Marketing Specialist', color: 'pink' },
    { id: 'david', name: 'David', role: 'Customer Experience Designer', color: 'green' },
    { id: 'priya', name: 'Priya', role: 'Marketing Analytics Manager', color: 'orange' },
    { id: 'alex', name: 'Alex', role: 'Growth Marketing Lead', color: 'indigo' },
  ];

  // Add this for debugging in development
  if (process.env.NODE_ENV === 'development') {
    window.debugSocket = () => {
      console.log('Socket info:', {
        connected: socketRef.current?.connected,
        id: socketRef.current?.id,
        transport: socketRef.current?.io?.engine?.transport?.name,
        messages: messages.length,
        isLoading,
        conversationId
      });
    };
    console.log('Debug helper available: window.debugSocket()');
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Connection Status Banner */}
      {!isConnected && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
          <p className="text-yellow-800 text-sm flex items-center">
            <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Connecting to Marketing Swarm server...
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Agent Panel */}
        <div className="lg:col-span-1">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Marketing Team</h2>
          <div className="space-y-3">
            {agents.map((agent) => (
              <AgentCard 
                key={agent.id}
                agent={agent}
                isActive={activeAgent === agent.id}
                hasWebData={messages.some(m => m.agent === agent.id && m.has_web_data)}
              />
            ))}
          </div>
        </div>

        {/* Conversation Panel */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            {/* Query Input */}
            <div className="p-6 border-b border-gray-200">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                    Ask your marketing question
                  </label>
                  <div className="relative">
                    <textarea
                      id="query"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="E.g., How should we launch our new robo-advisor to compete with Betterment?"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                      rows="3"
                      disabled={isLoading || !isConnected}
                    />
                    <button
                      type="submit"
                      disabled={!query.trim() || isLoading || !isConnected}
                      className={`
                        absolute bottom-3 right-3 p-2 rounded-lg transition-colors
                        ${query.trim() && !isLoading && isConnected
                          ? 'bg-primary-600 text-white hover:bg-primary-700'
                          : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        }
                      `}
                    >
                      <PaperAirplaneIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Example Queries */}
                <div className="flex items-center space-x-2 text-sm">
                  <SparklesIcon className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-500">Try:</span>
                  <div className="flex flex-wrap gap-2">
                    {exampleQueries.slice(0, 2).map((example, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setQuery(example)}
                        className="text-primary-600 hover:text-primary-700 hover:underline truncate max-w-xs"
                        disabled={isLoading || !isConnected}
                      >
                        {example.substring(0, 40)}...
                      </button>
                    ))}
                  </div>
                </div>
              </form>
            </div>

            {/* Live Feed */}
            <div 
              ref={feedRef}
              className="h-[600px] overflow-y-auto custom-scrollbar p-6"
            >
              {messages.length === 0 && !isLoading ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="mb-2">Ask a marketing question to start the team discussion</p>
                  <p className="text-sm">The agents will analyze, discuss, and provide strategic recommendations</p>
                </div>
              ) : (
                <LiveFeed 
                  messages={messages}
                  conversationId={conversationId}
                />
              )}
              
              {isLoading && messages.length === 0 && (
                <div className="flex justify-center py-8">
                  <TypingIndicator />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationInterface;