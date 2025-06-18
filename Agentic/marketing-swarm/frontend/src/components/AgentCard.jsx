import React from 'react';
import { motion } from 'framer-motion';
import { GlobeAltIcon } from '@heroicons/react/24/outline';

const AgentCard = ({ agent, isActive, hasWebData }) => {
  const getAgentInitial = (name) => name.charAt(0).toUpperCase();
  
  return (
    <motion.div
      animate={{
        scale: isActive ? 1.05 : 1,
        transition: { duration: 0.2 }
      }}
      className={`
        relative p-4 rounded-lg border transition-all
        ${isActive 
          ? 'border-primary-400 bg-primary-50 shadow-md' 
          : 'border-gray-200 bg-white hover:border-gray-300'
        }
      `}
    >
      <div className="flex items-start space-x-3">
        {/* Avatar */}
        <div className={`agent-avatar agent-${agent.id}`}>
          {getAgentInitial(agent.name)}
        </div>
        
        {/* Info */}
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{agent.name}</h3>
          <p className="text-sm text-gray-600">{agent.role}</p>
        </div>
        
        {/* Status Indicators */}
        <div className="flex items-center space-x-2">
          {hasWebData && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="text-primary-600"
              title="Using real-time data"
            >
              <GlobeAltIcon className="w-4 h-4" />
            </motion.div>
          )}
          
          {isActive && (
            <motion.div
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-2 h-2 bg-green-500 rounded-full"
              title="Active"
            />
          )}
        </div>
      </div>
      
      {/* Thinking Indicator */}
      {isActive && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute -bottom-2 left-1/2 transform -translate-x-1/2"
        >
          <div className="bg-white px-2 py-1 rounded-full shadow-sm border border-gray-200">
            <div className="flex space-x-1">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default AgentCard;