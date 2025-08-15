import { useState } from "react";
import { useChatbot } from "@/hooks/use-chatbot";
import Sidebar from "@/components/chatbot/sidebar";
import ChatArea from "@/components/chatbot/chat-area";
import MessageInput from "@/components/chatbot/message-input";

export default function Chatbot() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { 
    currentConversation, 
    messages, 
    isLoading, 
    isTyping, 
    sendMessage,
    setCurrentConversation,
    error
  } = useChatbot();

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Determine if the input should be disabled
  const isInputDisabled = isLoading || !!error || !currentConversation;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      {sidebarOpen && (
        <Sidebar 
          isOpen={sidebarOpen}
          onClose={handleSidebarClose}
          currentConversation={currentConversation}
          onConversationSelect={setCurrentConversation}
        />
      )}
      
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={handleSidebarClose}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Navigation */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 lg:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button 
                onClick={handleSidebarToggle}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                title="Toggle sidebar"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 ${error ? 'bg-red-500' : 'bg-green-500'} rounded-full ${!error && 'animate-pulse'}`}></div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {currentConversation?.title || "New Conversation"}
                  </h2>
                  <p className="text-sm text-gray-500">
                    {error ? 'Connection error' : 'AI Assistant is online'}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button 
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                title="Export conversation"
                disabled={!currentConversation || isLoading}
              >
                <svg className={`w-4 h-4 ${(!currentConversation || isLoading) ? 'text-gray-300' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </button>
              <button 
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                title="Share conversation"
                disabled={!currentConversation || isLoading}
              >
                <svg className={`w-4 h-4 ${(!currentConversation || isLoading) ? 'text-gray-300' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                </svg>
              </button>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <ChatArea 
          messages={messages}
          isLoading={isLoading}
          isTyping={isTyping}
          error={error}
          conversationId={currentConversation?.id}
        />

        {/* Message Input */}
        <MessageInput 
          onSendMessage={sendMessage}
          disabled={isInputDisabled}
          placeholder={error ? "Please fix connection errors before sending messages" : "Type a message..."}
        />
      </div>
    </div>
  );
}
