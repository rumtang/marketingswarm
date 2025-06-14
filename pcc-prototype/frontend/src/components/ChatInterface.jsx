import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Bot, User } from 'lucide-react';

export function ChatInterface() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m the Patient Concierge. How can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setMessage('');
    setIsTyping(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          context: {
            timestamp: new Date().toISOString(),
          },
        }),
      });

      const data = await response.json();

      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        content: data.response,
        timestamp: new Date(),
        suggestedActions: data.suggested_actions,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: messages.length + 2,
        type: 'bot',
        content: 'I apologize, but I\'m having trouble connecting. Please try again later.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-hospital-blue text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors z-50"
      >
        <MessageSquare className="w-6 h-6" />
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 bg-white rounded-lg shadow-2xl z-50 flex flex-col h-[500px]">
          {/* Header */}
          <div className="bg-hospital-blue text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold flex items-center gap-2">
              <Bot className="w-5 h-5" />
              Patient Concierge
            </h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-blue-700 p-1 rounded"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    msg.type === 'user'
                      ? 'bg-hospital-blue text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {msg.type === 'bot' && <Bot className="w-4 h-4 mt-0.5" />}
                    <div>
                      <p className="text-sm">{msg.content}</p>
                      {msg.suggestedActions && (
                        <div className="mt-2 space-y-1">
                          {msg.suggestedActions.map((action, idx) => (
                            <button
                              key={idx}
                              className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded hover:bg-opacity-30 transition-colors"
                              onClick={() => setMessage(action)}
                            >
                              {action}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    {msg.type === 'user' && <User className="w-4 h-4 mt-0.5" />}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4" />
                    <span className="text-sm">Typing...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-hospital-blue"
              />
              <button
                onClick={sendMessage}
                disabled={!message.trim()}
                className="bg-hospital-blue text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}