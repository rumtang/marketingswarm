import React from 'react';

const TypingIndicator = () => {
  return (
    <div className="flex items-center space-x-2 text-gray-500">
      <span className="text-sm">Agents are thinking</span>
      <div className="flex space-x-1">
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
      </div>
    </div>
  );
};

export default TypingIndicator;