import { useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { useGetConverstionById, useCreateConversation, useDeleteConversation } from "../../api";
import { useAdminUser } from "../../api/users";
import { Conversation } from "../../interfaces";


interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentConversation: Conversation | null;
  onConversationSelect: (conversation: Conversation | null) => void;
}

export default function Sidebar({ isOpen, onClose, currentConversation, onConversationSelect }: SidebarProps) {
  const queryClient = useQueryClient();
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  // Fetch admin user ID from API or use environment variable fallback
  const { data: adminUserData, isLoading: isAdminUserLoading } = useAdminUser();
  const [ userId, setUserId ] = useState<string | null>(null);
  
  // Set userId when admin user data is loaded
  useEffect(() => {
    if (adminUserData?.userId) {
      setUserId(adminUserData.userId);
      console.log("Using admin user ID:", adminUserData.userId);
    }
  }, [adminUserData]);

  const { data: conversations = [], isLoading: isConversationsLoading } = useGetConverstionById(userId ?? "");  

  // Debug: Log conversations whenever they change
  useEffect(() => {
    console.log("Conversations in sidebar:", conversations);
    
    // Auto-select first conversation if we have conversations but none is selected
    if (conversations.length > 0 && !currentConversation) {
      console.log("Auto-selecting first conversation:", conversations[0]);
      onConversationSelect(conversations[0]);
    } else if (conversations.length === 0 && currentConversation) {
      // If there are no conversations left but we still have a selected conversation
      // (this can happen after deleting the last conversation)
      console.log("No conversations left, clearing selection");
      onConversationSelect(null);
    }
  }, [conversations, currentConversation, onConversationSelect]);

  const { 
    mutate: createConversationMutate, 
    isPending: isCreatingConversation,
    isSuccess: isConversationCreated, 
    isError: isConversationError, 
    error: conversationError, 
    data: conversationData 
  } = useCreateConversation((newConversation) => {
    onConversationSelect(newConversation);
  });

  const { 
    mutate: useDeleteConversationMutate, 
    isPending: isDeletingConversation,
    isSuccess: isConversationDeleted
  } = useDeleteConversation((deletedId) => {
    // If we just deleted the currently selected conversation
    if (currentConversation?.id === deletedId) {
      // Find another conversation to select, or set to null if none left
      if (conversations.length > 1) {
        // Find the first conversation that's not the one we just deleted
        const nextConversation = conversations.find(c => c.id !== deletedId);
        if (nextConversation) {
          console.log("Selecting next available conversation after deletion:", nextConversation);
          onConversationSelect(nextConversation);
        } else {
          onConversationSelect(null);
        }
      } else {
        // If we just deleted the last conversation, set to null
        console.log("No conversations left after deletion");
        onConversationSelect(null);
      }
    }
  });


  const handleNewConversation = () => {
    console.log("Creating new conversation for user:", userId);
    createConversationMutate({
      userId: userId ?? "",
      title: `New Chat ${new Date().toLocaleTimeString()}`
    });
  };

 const handleDeleteConversation = (conversationId: string) => {
    if (deleteConfirm === conversationId) {
      // If already confirmed, proceed with deletion
      useDeleteConversationMutate(conversationId);
      // Clear the confirmation state
      setDeleteConfirm(null);
    } else {
      // Set confirmation for this conversation
      setDeleteConfirm(conversationId);
      
      // Auto-clear confirmation after 5 seconds
      setTimeout(() => {
        setDeleteConfirm((current) => current === conversationId ? null : current);
      }, 5000);
    }
  }; 

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-80 bg-white shadow-xl border-r border-gray-200 lg:relative lg:w-80 lg:z-auto lg:shadow-none"
    >
      <div className="flex flex-col h-full">
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-emerald-500 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">AI Assistant</h1>
              <p className="text-sm text-gray-500">Always here to help</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            title="Close sidebar"
          >
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <div className="mb-6">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Conversations {isConversationsLoading ? "(Loading...)" : `(${conversations.length})`}
            </h2>
            <div className="space-y-1">
              {isConversationsLoading ? (
                <div className="p-3 text-sm text-gray-500">Loading conversations...</div>
              ) : conversations.length === 0 ? (
                <div className="p-3 text-sm text-gray-500">No conversations yet. Create a new one!</div>
              ) : (
                conversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    onClick={() => {
                      console.log("Selected conversation:", conversation);
                      onConversationSelect(conversation);
                      // Keep sidebar open - let user control it with toggle buttons
                    }}
                    className={`w-full text-left p-3 rounded-lg transition-all duration-200 group ${
                      currentConversation?.id === conversation.id
                        ? 'bg-blue-50 border border-blue-200 text-blue-700'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 min-w-0">
                        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                          currentConversation?.id === conversation.id ? 'bg-blue-600' : 'bg-gray-300'
                        }`}></div>
                        <span className="text-sm font-medium truncate">{conversation.title}</span>
                      </div>
                      <span className="text-xs text-gray-400 flex-shrink-0">
                        {conversation.updatedAt ? new Date(conversation.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'New'}
                      </span>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteConversation(conversation.id);
                        }}
                        className={`p-1 rounded hover:bg-red-100 transition-colors ${
                          deleteConfirm === conversation.id ? 'bg-red-100 text-red-600' : 'text-gray-400 hover:text-red-500'
                        }`}
                        title={deleteConfirm === conversation.id ? "Click again to confirm deletion" : "Delete conversation"}
                        disabled={isDeletingConversation}
                      >
                        {isDeletingConversation && deleteConfirm === conversation.id ? (
                          <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="mb-6">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Quick Actions</h2>
            <div className="space-y-1">
              <button 
                onClick={handleNewConversation}
                disabled={isCreatingConversation}
                className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-3 disabled:opacity-50"
              >
                {isCreatingConversation ? (
                  <svg className="w-4 h-4 text-gray-500 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                )}
                <span className="text-sm text-gray-700">
                  {isCreatingConversation ? "Creating..." : "New Conversation"}
                </span>
              </button>
              <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-3">
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
                <span className="text-sm text-gray-700">Browse Templates</span>
              </button>
              <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-3">
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm text-gray-700">Chat History</span>
              </button>
            </div>
          </div>
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm font-medium">JD</span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-900 truncate">John Doe</p>
              <p className="text-xs text-gray-500 truncate">john@example.com</p>
            </div>
            <button className="p-1 hover:bg-gray-200 rounded transition-colors">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
