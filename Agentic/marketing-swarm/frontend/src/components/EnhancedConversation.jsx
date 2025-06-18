import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, SparklesIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import io from 'socket.io-client';

import AgentCard from './AgentCard';
import LiveFeed from './LiveFeed';
import TypingIndicator from './TypingIndicator';
import BriefingDocument from './BriefingDocument';
import { startConversation } from '../services/api';

const EnhancedConversation = ({ isDemoMode }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeAgent, setActiveAgent] = useState(null);
  const [currentPhase, setCurrentPhase] = useState('');
  const [phaseGoal, setPhaseGoal] = useState('');
  const [briefingDocument, setBriefingDocument] = useState(null);
  const [showBriefing, setShowBriefing] = useState(false);
  
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

  // Phase colors for visual feedback
  const phaseColors = {
    'Discovery & Situation Analysis': 'bg-blue-100 text-blue-800',
    'Analysis & Insights': 'bg-purple-100 text-purple-800',
    'Strategic Recommendations': 'bg-green-100 text-green-800',
    'Final Synthesis': 'bg-orange-100 text-orange-800'
  };

  useEffect(() => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
    
    socketRef.current = io(apiUrl, {
      transports: ['websocket', 'polling'],
    });

    socketRef.current.on('connection_established', (data) => {
      console.log('WebSocket connected:', data);
    });

    socketRef.current.on('conversation_started', (data) => {
      console.log('Conversation started:', data);
      toast.success(data.goal || 'Marketing team collaboration started');
      setCurrentPhase('Discovery & Situation Analysis');
      setPhaseGoal('Understanding the challenge and current state');
    });

    socketRef.current.on('conversation_phase', (data) => {
      console.log('Phase transition:', data);
      setCurrentPhase(data.phase);
      setPhaseGoal(data.goal);
      toast.info(`Moving to ${data.phase}`);
    });

    socketRef.current.on('agent_response', (data) => {
      console.log('Agent response:', data);
      setMessages(prev => [...prev, data]);
      setActiveAgent(data.agent);
      
      // Clear typing indicator after response
      setTimeout(() => setActiveAgent(null), 500);
    });

    socketRef.current.on('conversation_complete', (data) => {
      setIsLoading(false);
      console.log('Conversation complete:', data);
      
      // Clear timeout on completion
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      // Set briefing document if available
      if (data.briefing_document) {
        setBriefingDocument(data.briefing_document);
        setShowBriefing(true);
        toast.success('One-page briefing document ready!', {
          duration: 5000,
          icon: '📄'
        });
      } else {
        toast.success(`Conversation completed in ${Math.round(data.duration)}s`);
      }
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
    setActiveAgent(null);
    setBriefingDocument(null);
    setShowBriefing(false);
    setCurrentPhase('');
    setPhaseGoal('');

    try {
      const response = await startConversation(query, isDemoMode);
      setConversationId(response.conversation_id);
      
      // Join the conversation room
      socketRef.current.emit('join_conversation', {
        conversation_id: response.conversation_id,
        query: query
      });

      // Set a timeout for long-running conversations
      timeoutRef.current = setTimeout(() => {
        setIsLoading(false);
        toast.error('Conversation timed out. Please try again.');
      }, 180000); // 3 minutes timeout

    } catch (error) {
      setIsLoading(false);
      toast.error('Failed to start conversation');
      console.error('Error starting conversation:', error);
    }
  };

  const handleExampleClick = (example) => {
    setQuery(example);
  };

  const handlePrintBriefing = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Marketing Strategy Collaboration
            </h1>
            {showBriefing && (
              <button
                onClick={() => setShowBriefing(false)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Back to Conversation
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      {showBriefing && briefingDocument ? (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <BriefingDocument 
            briefing={briefingDocument} 
            onPrint={handlePrintBriefing}
          />
        </div>
      ) : (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Sidebar - Query Input */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Marketing Challenge
                </h2>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Describe your marketing challenge..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={4}
                    disabled={isLoading}
                  />
                  
                  <button
                    type="submit"
                    disabled={isLoading || !query.trim()}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        Building Strategy...
                      </>
                    ) : (
                      <>
                        <PaperAirplaneIcon className="h-5 w-5" />
                        Start Strategic Discussion
                      </>
                    )}
                  </button>
                </form>

                {/* Example Queries */}
                <div className="mt-6">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">
                    Example challenges:
                  </h3>
                  <div className="space-y-2">
                    {exampleQueries.map((example, index) => (
                      <button
                        key={index}
                        onClick={() => handleExampleClick(example)}
                        className="w-full text-left px-3 py-2 text-sm text-gray-600 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                      >
                        <SparklesIcon className="inline h-4 w-4 mr-1 text-yellow-500" />
                        {example}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Current Phase Indicator */}
                {currentPhase && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Current Phase:
                    </h3>
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${phaseColors[currentPhase] || 'bg-gray-100 text-gray-800'}`}>
                      {currentPhase}
                    </div>
                    {phaseGoal && (
                      <p className="mt-2 text-sm text-gray-600">
                        Goal: {phaseGoal}
                      </p>
                    )}
                  </div>
                )}

                {/* Final Document Button */}
                {briefingDocument && !showBriefing && (
                  <div className="mt-6">
                    <button
                      onClick={() => setShowBriefing(true)}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <DocumentTextIcon className="h-5 w-5" />
                      View Strategic Brief
                    </button>
                  </div>
                )}
              </div>

              {/* Active Agents */}
              <div className="mt-6 bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Marketing Team
                </h3>
                <div className="space-y-3">
                  {['sarah', 'marcus', 'elena', 'david', 'priya', 'alex'].map((agentId) => (
                    <AgentCard
                      key={agentId}
                      agentId={agentId}
                      isActive={activeAgent === agentId}
                      hasSpoken={messages.some(m => m.agent === agentId)}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Right Side - Conversation Feed */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-md h-[800px] flex flex-col">
                <div className="px-6 py-4 border-b">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Strategic Discussion
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Team collaborating to create one-page strategic brief
                  </p>
                </div>
                
                <div 
                  ref={feedRef}
                  className="flex-1 overflow-y-auto p-6"
                >
                  {messages.length === 0 && !isLoading && (
                    <div className="text-center py-12">
                      <p className="text-gray-500">
                        Start a conversation to see the marketing team collaborate on your strategic brief.
                      </p>
                    </div>
                  )}
                  
                  <LiveFeed messages={messages} />
                  
                  {activeAgent && (
                    <TypingIndicator agentId={activeAgent} />
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedConversation;