import { useState, useEffect } from "react";
import { Conversation } from "../interfaces";
import { useQueryClient } from "@tanstack/react-query";
import { useGetConverstionById, useGetMessages, useCreateMessage } from "../api";
import { useAdminUser } from "../api/users";

export function useChatbot() {
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Get admin user ID
  const { 
    data: adminUserData, 
    isLoading: isAdminUserLoading, 
    error: adminUserError 
  } = useAdminUser();
  
  const [ userId, setUserId ] = useState<string | null>(null);
  
  // Set userId when admin user data is loaded
  useEffect(() => {
    if (adminUserData?.userId) {
      setUserId(adminUserData.userId);
      console.log("useChatbot: Using admin user ID:", adminUserData.userId);
      setError(null); // Clear any previous errors when we get a user ID
    }
  }, [adminUserData]);

  // Handle admin user error
  useEffect(() => {
    if (adminUserError) {
      const errorMessage = adminUserError instanceof Error 
        ? adminUserError.message 
        : 'Failed to load admin user';
      console.error("Admin user error:", errorMessage);
      setError(`Admin user error: ${errorMessage}`);
    }
  }, [adminUserError]);
  
  const { 
    data: conversations = [], 
    isLoading: isConversationsLoading,
    error: conversationsError
  } = useGetConverstionById(userId ?? "");

  // Handle conversations error
  useEffect(() => {
    if (conversationsError && userId) {
      const errorMessage = conversationsError instanceof Error 
        ? conversationsError.message 
        : 'Failed to load conversations';
      console.error("Conversations error:", errorMessage);
      setError(`Conversations error: ${errorMessage}`);
    }
  }, [conversationsError, userId]);

  useEffect(() => {
    if (conversations.length > 0 && !currentConversation) {
      setCurrentConversation(conversations[0]);
      setError(null); // Clear errors when we successfully load conversations
    }
  }, [conversations, currentConversation]);

  // Get messages for current conversation
  const { 
    data: messages = [], 
    isLoading: isMessagesLoading,
    error: messagesError
  } = useGetMessages(currentConversation?.id);

  // Handle messages error
  useEffect(() => {
    if (messagesError && currentConversation?.id) {
      const errorMessage = messagesError instanceof Error 
        ? messagesError.message 
        : 'Failed to load messages';
      console.error("Messages error:", errorMessage);
      setError(`Messages error: ${errorMessage}`);
    }
  }, [messagesError, currentConversation?.id]);

  const createMessageMutation = useCreateMessage();

  // Handle message creation error
  useEffect(() => {
    if (createMessageMutation.error) {
      const errorMessage = createMessageMutation.error instanceof Error 
        ? createMessageMutation.error.message 
        : 'Failed to send message';
      console.error("Message creation error:", errorMessage);
      setError(`Failed to send message: ${errorMessage}`);
    }
  }, [createMessageMutation.error]);

  // Handle successful message creation
  useEffect(() => {
    if (createMessageMutation.isSuccess) {
      // Clear any previous errors on successful message send
      setError(null);
      
      // Simulate bot response delay
      setIsTyping(true);
      setTimeout(() => {
        setIsTyping(false);
        queryClient.invalidateQueries({
          queryKey: ["messages", currentConversation?.id],
        });
      }, 3000);
    }
  }, [createMessageMutation.isSuccess, currentConversation?.id, queryClient]);

  const sendMessage = (content: string) => {
    if (!currentConversation?.id) {
      setError("Cannot send message: No active conversation");
      return;
    }
    
    createMessageMutation.mutate({
      conversationId: currentConversation.id,
      content,
      isBot: false,
    });
  };

  const isLoading = isAdminUserLoading || isConversationsLoading || isMessagesLoading;

  return {
    currentConversation,
    setCurrentConversation,
    messages,
    isLoading,
    isTyping,
    sendMessage,
    error,
    userId,
  };
}
