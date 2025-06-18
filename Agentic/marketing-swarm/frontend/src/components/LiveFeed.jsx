import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';
import { GlobeAltIcon, ClockIcon } from '@heroicons/react/24/outline';

const LiveFeed = ({ messages, conversationId }) => {
  const getAgentColor = (agentId) => {
    const colors = {
      sarah: 'border-purple-200 bg-purple-50',
      marcus: 'border-blue-200 bg-blue-50',
      elena: 'border-pink-200 bg-pink-50',
      david: 'border-green-200 bg-green-50',
      priya: 'border-orange-200 bg-orange-50',
      alex: 'border-indigo-200 bg-indigo-50',
    };
    return colors[agentId] || 'border-gray-200 bg-gray-50';
  };

  const getAgentInfo = (agentId) => {
    const agents = {
      sarah: { name: 'Sarah', role: 'Brand Strategy Lead' },
      marcus: { name: 'Marcus', role: 'Digital Campaign Manager' },
      elena: { name: 'Elena', role: 'Content Marketing Specialist' },
      david: { name: 'David', role: 'Customer Experience Designer' },
      priya: { name: 'Priya', role: 'Marketing Analytics Manager' },
      alex: { name: 'Alex', role: 'Growth Marketing Lead' },
    };
    return agents[agentId] || { name: 'Unknown', role: 'Agent' };
  };

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {messages.map((message, index) => {
          const agentInfo = getAgentInfo(message.agent);
          const timestamp = new Date(message.timestamp);
          
          return (
            <motion.div
              key={`${conversationId}-${index}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={`rounded-lg border p-4 ${getAgentColor(message.agent)}`}
            >
              {/* Agent Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`agent-avatar agent-${message.agent}`}>
                    {agentInfo.name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{agentInfo.name}</h4>
                    <p className="text-xs text-gray-600">{agentInfo.role}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  {message.has_web_data && (
                    <div className="flex items-center space-x-1 text-primary-600">
                      <GlobeAltIcon className="w-3 h-3" />
                      <span>Live data</span>
                    </div>
                  )}
                  {message.thinking_time > 0 && (
                    <div className="flex items-center space-x-1">
                      <ClockIcon className="w-3 h-3" />
                      <span>{message.thinking_time}s</span>
                    </div>
                  )}
                  <span>{format(timestamp, 'HH:mm:ss')}</span>
                </div>
              </div>
              
              {/* Message Content */}
              <div className="text-gray-800 whitespace-pre-wrap">
                {message.message}
              </div>
              
              {/* Data Indicator */}
              {message.has_web_data && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-600 flex items-center">
                    <GlobeAltIcon className="w-3 h-3 mr-1" />
                    This response includes current market data and trends
                  </p>
                </div>
              )}
            </motion.div>
          );
        })}
      </AnimatePresence>
      
      {conversationId && messages.length > 0 && (
        <div className="text-center py-4">
          <p className="text-sm text-gray-500">
            Conversation ID: {conversationId}
          </p>
        </div>
      )}
    </div>
  );
};

export default LiveFeed;