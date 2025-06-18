import React, { useState, useRef, useEffect } from 'react';
// import { motion, AnimatePresence } from 'framer-motion'; // TODO: Add animations later
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
  const socketRef = useRef(null);
  const feedRef = useRef(null);
  const timeoutRef = useRef(null);

  // Example queries
  const exampleQueries = [
    "How should we launch our new robo-advisor to compete with Betterment?",
    "Our customer acquisition cost has doubled. What's our action plan?",
    "How do we market complex derivatives to retail investors compliantly?",
    "We need a content strategy that builds trust with Gen Z about retirement planning.",
  ];

  useEffect(() => {
    // Initialize socket connection - use the same URL as API
    const socketUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
    socketRef.current = io(socketUrl, {
      transports: ['websocket'],
    });

    socketRef.current.on('connect', () => {
      console.log('Connected to backend');
    });

    socketRef.current.on('agent_response', (data) => {
      console.log('Received agent response:', data);
      setMessages(prev => [...prev, data]);
      setActiveAgent(data.agent);
      
      // Clear timeout on first response
      if (timeoutRef.current && messages.length === 0) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      // Clear active agent after response
      setTimeout(() => setActiveAgent(null), 1000);
    });

    socketRef.current.on('conversation_complete', (data) => {
      setIsLoading(false);
      // Clear timeout if conversation completes
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      toast.success(`Conversation completed in ${Math.round(data.duration)}s`);
    });

    socketRef.current.on('conversation_error', (data) => {
      setIsLoading(false);
      // Clear timeout on error
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      toast.error(`Error: ${data.error}`);
    });

    socketRef.current.on('joined_conversation', (data) => {
      console.log('Successfully joined conversation:', data);
    });

    return () => {
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

    setIsLoading(true);
    setMessages([]);
    setConversationId(null);

    try {
      const response = await startConversation(query, isDemoMode);
      
      if (response.status === 'blocked') {
        toast.error('Query contains non-compliant content');
        setIsLoading(false);
        return;
      }

      setConversationId(response.conversation_id);
      
      // Join conversation room
      console.log('Joining conversation:', response.conversation_id, 'with query:', query);
      socketRef.current.emit('join_conversation', {
        conversation_id: response.conversation_id,
        query: query  // Pass the query to backend
      });

      toast.success('Marketing team is analyzing your query...');
      
      // Set a timeout to detect if no responses are received
      timeoutRef.current = setTimeout(() => {
        if (messages.length === 0) {
          toast.error('No response from agents. Please try again.');
          setIsLoading(false);
        }
      }, 15000); // 15 second timeout
    } catch (error) {
      console.error('Failed to start conversation:', error);
      toast.error('Failed to start conversation');
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

  return (
    <div className="max-w-7xl mx-auto">
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
                      disabled={isLoading}
                    />
                    <button
                      type="submit"
                      disabled={!query.trim() || isLoading}
                      className={`
                        absolute bottom-3 right-3 p-2 rounded-lg transition-colors
                        ${query.trim() && !isLoading
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
                        disabled={isLoading}
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