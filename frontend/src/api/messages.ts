import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Message } from "../interfaces";

// Define API_BASE with explicit URL to ensure correct connection
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
console.log("Messages API_BASE set to:", API_BASE);

interface GetMessagesParams {
    conversationId: string | number;
}

export const getMessages = async ({ conversationId }: GetMessagesParams): Promise<Message[]> => {
    console.log(`Fetching messages for conversation: ${conversationId} from ${API_BASE}/messages/${conversationId}`);
    try {
        const response = await fetch(`${API_BASE}/messages/${conversationId}`);
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API Error (${response.status}): ${errorText}`);
            
            // For 404 "no messages", return empty array instead of throwing
            if (response.status === 404 && errorText.includes("No messages found")) {
                return [];
            }
            
            throw new Error(`Network response was not ok: ${response.status} ${errorText}`);
        }
        
        // Get the raw data from the response
        const rawData = await response.json();
        console.log("Raw message data:", rawData);
        
        // Transform snake_case to camelCase
        const transformedData = Array.isArray(rawData) ? rawData.map(msg => ({
            id: msg.id,
            conversationId: msg.conversation_id,
            content: msg.content,
            isBot: msg.is_bot,
            createdAt: msg.created_at
        })) : [];
        
        console.log("Transformed message data:", transformedData);
        
        return transformedData;
    } catch (error) {
        console.error("Error fetching messages:", error);
        return [];
    }
};


export const useGetMessages = (
    conversationId: string | number | undefined
) => {
    return useQuery({
        queryKey: ["messages", conversationId],
        queryFn: async () => {
            if (!conversationId) return [];
            const response = await getMessages({ conversationId });
            return response;
        },
        enabled: !!conversationId, // Only run if conversationId is available
    });
};

export const createMessage = async ({ conversationId, content, isBot }: { conversationId: any; content: any; isBot: any }) => {
  console.log(`Creating message for conversation: ${conversationId} at ${API_BASE}/messages`);
  try {
    const response = await fetch(`${API_BASE}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        content,
        is_bot: isBot,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error (${response.status}): ${errorText}`);
      throw new Error(`Network response was not ok: ${response.status} ${errorText}`);
    }
    return response.json();
  } catch (error) {
    console.error("Error creating message:", error);
    throw error;
  }
};

export const useCreateMessage = () => {
    const queryClient = useQueryClient();
    
    return useMutation({
        mutationFn: createMessage,
        onSuccess: (_, variables) => {
            // Invalidate messages to refetch
            queryClient.invalidateQueries({
                queryKey: ["messages", variables.conversationId]
            });
            
            // Generate automatic bot response if the message is from the user
            if (!variables.isBot) {
                setTimeout(async () => {
                    const botResponses = [
                        "That's a great question! Let me help you with that.",
                        "I understand what you're looking for. Here's what I can suggest:",
                        "Thanks for asking! Based on your question, I'd recommend:",
                        "Great point! Let me break this down for you:",
                        "I'm here to help! For your specific needs, consider this approach:"
                    ];
                    
                    const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)];
                    
                    try {
                        await createMessage({
                            conversationId: variables.conversationId,
                            content: randomResponse,
                            isBot: true
                        });
                        
                        // Invalidate again to show the bot response
                        queryClient.invalidateQueries({
                            queryKey: ["messages", variables.conversationId]
                        });
                    } catch (error) {
                        console.error("Error creating bot response:", error);
                    }
                }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
            }
        },
        onError: (error: Error) => {
            console.error("Error creating message:", error);
        }
    });
};