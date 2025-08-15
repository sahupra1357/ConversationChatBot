import { useEffect, useRef } from "react";
import { Message } from "../../interfaces";
import MessageBubble from "./message-bubble";

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  isTyping: boolean;
  error?: string | null;
  conversationId?: string;
}

export default function ChatArea({ 
  messages, 
  isLoading, 
  isTyping, 
  error, 
  conversationId 
}: ChatAreaProps) {
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Show loading state when we're waiting for initial data
  if (isLoading && messages.length === 0 && !error) {
    return (
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto p-4 lg:p-6 flex items-center justify-center">
          <div className="text-center p-6 max-w-md">
            <div className="w-12 h-12 border-4 border-t-blue-500 border-gray-200 rounded-full animate-spin mx-auto mb-4"></div>
            <h3 className="text-lg font-medium text-gray-900">Loading conversation...</h3>
            <p className="text-sm text-gray-500 mt-2">Please wait while we retrieve your messages.</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && messages.length === 0) {
    return (
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto p-4 lg:p-6 flex items-center justify-center">
          <div className="text-center p-6 max-w-md bg-red-50 rounded-lg border border-red-200">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-red-800">Error Loading Conversation</h3>
            <p className="text-sm text-red-600 mt-2">{error}</p>
            <p className="text-xs text-gray-500 mt-4">
              {conversationId ? `Conversation ID: ${conversationId}` : 'No conversation selected'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-hidden">
      <div className="h-full overflow-y-auto p-4 lg:p-6 space-y-6">
        {/* Welcome Message */}
        {messages.length === 0 && !isLoading && !error && (
          <div className="flex justify-center">
            <div className="max-w-md text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Welcome to AI Assistant!</h3>
              <p className="text-gray-600 text-sm">I'm here to help you with any questions or tasks. Feel free to ask me anything!</p>
            </div>
          </div>
        )}

        {/* Messages */}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex items-start space-x-3 animate-fade-in">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="flex-1 max-w-3xl">
              <div className="bg-white rounded-2xl rounded-tl-md shadow-sm border border-gray-200 p-4">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                  <span className="text-gray-500 text-sm">AI is typing...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>
    </div>
  );
}
