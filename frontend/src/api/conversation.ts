import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Conversation } from "../interfaces";


// Define API_BASE with explicit URL to ensure correct connection
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
console.log("API_BASE set to:", API_BASE);

interface GetConversationsResponse {
    conversations: Conversation[];
}

export const getConversationsByUserId = async (userId: string): Promise<GetConversationsResponse> => {
    if (!userId || userId.trim() === "") {
        console.log("No user ID provided, returning empty conversations list");
        return { conversations: [] };
    }

    console.log(`Fetching conversations for user: ${userId} from ${API_BASE}/conversations/user/${userId}`);
    try {
        const response: Response = await fetch(`${API_BASE}/conversations/user/${userId}`);

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API Error (${response.status}): ${errorText}`);
            
            // For 404 "no conversations", return empty array instead of throwing
            if (response.status === 404 && errorText.includes("No conversations found")) {
                return { conversations: [] };
            }
            
            throw new Error(`Network response was not ok: ${response.status} ${errorText}`);
        }
        
        // Get the raw data from the response
        const rawData = await response.json();
        console.log("Raw conversation data:", rawData);
        
        // Transform snake_case to camelCase
        const transformedData = Array.isArray(rawData) ? rawData.map(convo => ({
            id: convo.id,
            title: convo.title,
            userId: convo.user_id,
            createdAt: convo.created_at,
            updatedAt: convo.updated_at
        })) : [];
        
        console.log("Transformed conversation data:", transformedData);
        
        return { conversations: transformedData };
    } catch (error) {
        console.error("Error fetching conversations:", error);
        return { conversations: [] }; // Return empty list instead of throwing
    }
};

export const useGetConverstionById = (userId: string) => {
    return useQuery({
        queryKey: ["conversations", userId],
        queryFn: async () => {
            try {
                const response = await getConversationsByUserId(userId);
                return response.conversations || [];
            } catch (error) {
                console.error("Error in useGetConverstionById:", error);
                return [];
            }
        },
        enabled: !!userId && userId.trim() !== "", // Only run if userId is available and not empty
        retry: 3,
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
}

export const createConversation = async ({ userId, title }: { userId: string; title: string }): Promise<Conversation> => {
    const response = await fetch(`${API_BASE}/conversations`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId, title: title || `New Chat ${new Date().toLocaleTimeString()}` }),
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
};

export const useCreateConversation = (onConversationSelect?: (conversation: Conversation) => void) => {
    const queryClient = useQueryClient();
    
    return useMutation({
        mutationFn: async ({ userId, title }: { userId: string; title?: string }) => {
            if (!userId || userId.trim() === "") {
                throw new Error("Cannot create conversation: User ID is required");
            }
            
            console.log(`Creating conversation for user: ${userId} at ${API_BASE}/conversations`);
            try {
                const response = await fetch(`${API_BASE}/conversations`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        user_id: userId, 
                        title: title || `New Chat ${new Date().toLocaleTimeString()}` 
                    }),
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error(`API Error (${response.status}): ${errorText}`);
                    throw new Error(`Network response was not ok: ${response.status} ${errorText}`);
                }
                
                const data = await response.json();
                console.log("Created conversation:", data);
                return data;
            } catch (error) {
                console.error("Error creating conversation:", error);
                throw error;
            }
        },
        onSuccess: async (newConversation) => {
            // Invalidate conversations query to update the list
            queryClient.invalidateQueries({
                queryKey: ["conversations"]
            });
            
            // Select the newly created conversation if callback is provided
            if (onConversationSelect) {
                onConversationSelect(newConversation);
            }

            // Add welcome message if this is a "Getting Started Guide"
            if (newConversation.title === "Getting Started Guide") {
                setTimeout(async () => {
                    try {
                        await fetch(`${API_BASE}/messages`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                conversationId: newConversation.id,
                                content: "Welcome to your AI Assistant! I'm here to help you with questions, provide information, and assist with various tasks. Feel free to ask me anything to get started.",
                                isBot: true
                            }),
                        });
                        // Invalidate messages query to show the welcome message
                        queryClient.invalidateQueries({
                            queryKey: ["messages", newConversation.id]
                        });
                    } catch (error) {
                        console.error("Error adding welcome message:", error);
                    }
                }, 500);
            }
        },
        onError: (error: Error) => {
            console.error("Error creating conversation:", error);
        }
    });
};

export const deleteConversation = async (conversationId: string): Promise<void> => {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
};

export const useDeleteConversation = (
    onSuccess?: (deletedId: string) => void
) => {
    const queryClient = useQueryClient();
    
    return useMutation({
        mutationFn: async (conversationId: string) => {
            console.log('Deleting conversation:', conversationId);
            
            try {
                // First, delete all messages associated with this conversation
                console.log('Deleting all messages for conversation:', conversationId);
                const messagesResponse = await fetch(`${API_BASE}/messages/conversation/${conversationId}`, {
                    method: 'DELETE',
                });
                
                if (!messagesResponse.ok) {
                    const errorText = await messagesResponse.text();
                    console.error(`API Error deleting messages (${messagesResponse.status}): ${errorText}`);
                    // Continue with conversation deletion even if message deletion fails
                }
                
                // Then delete the conversation itself
                await deleteConversation(conversationId);
                console.log('Delete conversation successful');
                return conversationId;
            } catch (error) {
                console.error('Error in conversation deletion cascade:', error);
                throw error;
            }
        },
        onSuccess: async (deletedId) => {
            console.log('Delete successful, refreshing conversations');
            
            // Invalidate all conversation queries to update lists
            await queryClient.invalidateQueries({
                queryKey: ["conversations"]
            });
            
            // Invalidate messages for this conversation
            await queryClient.invalidateQueries({
                queryKey: ["messages", deletedId]
            });
            
            // Call the onSuccess callback if provided
            if (onSuccess) {
                onSuccess(deletedId);
            }
        },
        onError: (error: Error) => {
            console.error('Delete failed:', error);
        }
    });
};

