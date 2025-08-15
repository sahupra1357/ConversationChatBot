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
            
            // Generate AI response if the message is from the user
            if (!variables.isBot) {
                setTimeout(async () => {
                    try {
                        console.log(`Requesting AI response from ${API_BASE}/chat`);
                        
                        // Get all messages for context
                        const existingMessages = await queryClient.fetchQuery({
                            queryKey: ["messages", variables.conversationId],
                        }) as Message[] || [];
                        
                        // Simplify the message history to just the essential fields
                        const simplifiedHistory = Array.isArray(existingMessages) 
                            ? existingMessages.map((msg: Message) => ({
                                content: msg.content,
                                isBot: msg.isBot,
                                timestamp: msg.createdAt
                              })).slice(-10) // Only include the last 10 messages for context
                            : [];
                        
                        // Call the /chat API endpoint
                        console.log("Sending chat request with payload:", {
                            conversation_id: variables.conversationId,
                            message: variables.content,
                            message_history: simplifiedHistory
                        });
                        
                        const response = await fetch(`${API_BASE}/chat`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                conversation_id: variables.conversationId,
                                message: variables.content,
                                message_history: simplifiedHistory
                            }),
                        });
                        
                        if (!response.ok) {
                            const errorText = await response.text();
                            console.error(`Chat API Error (${response.status}): ${errorText}`);
                            
                            // For 422 errors, log more details to help debugging
                            if (response.status === 422) {
                                console.error("422 Validation Error. This usually means the request body doesn't match what the API expects.");
                                console.error("Request body was:", JSON.stringify({
                                    conversation_id: variables.conversationId,
                                    message: variables.content,
                                    message_history: existingMessages
                                }, null, 2));
                            }
                            
                            throw new Error(`Chat API response was not ok: ${response.status} ${errorText}`);
                        }
                        
                        const chatResponse = await response.json();
                        console.log("AI response received (raw):", JSON.stringify(chatResponse, null, 2));
                        
                        // Extract the response text, handling different response structures
                        let responseText = "";
                        
                        // Try multiple approaches to extract the text based on different response formats
                        if (typeof chatResponse === 'object') {
                            console.log("Response is an object, checking different properties");
                            
                            // Handle the specific nested structure from ReActAgent
                            if (chatResponse.response && 
                                typeof chatResponse.response === 'object' && 
                                chatResponse.response.response && 
                                typeof chatResponse.response.response === 'object') {
                                
                                console.log("Found nested response.response.blocks structure");
                                const nestedResponse = chatResponse.response.response;
                                
                                if (nestedResponse.blocks && Array.isArray(nestedResponse.blocks)) {
                                    console.log("Found blocks array with", nestedResponse.blocks.length, "blocks");
                                    const textBlocks = nestedResponse.blocks
                                        .filter((block: any) => block && block.block_type === 'text')
                                        .map((block: any) => block.text || '');
                                        
                                    console.log("Extracted text blocks:", textBlocks);
                                    responseText = textBlocks.join('\n\n');
                                }
                            }
                            // Option 1: Direct string response
                            else if (chatResponse.response && typeof chatResponse.response === 'string') {
                                console.log("Found direct string response");
                                responseText = chatResponse.response;
                            } 
                            // Option 2: Array of strings
                            else if (Array.isArray(chatResponse)) {
                                console.log("Response is an array");
                                responseText = chatResponse.map((item: any) => 
                                    typeof item === 'string' ? item : JSON.stringify(item)
                                ).join('\n\n');
                            }
                            // Option 3: Response property is an array
                            else if (Array.isArray(chatResponse.response)) {
                                console.log("Response.response is an array");
                                responseText = chatResponse.response.map((item: any) => 
                                    typeof item === 'string' ? item : JSON.stringify(item)
                                ).join('\n\n');
                            }
                            // Option 4: Nested object structure
                            else if (typeof chatResponse.response === 'object' && chatResponse.response !== null) {
                                console.log("Response has a nested object structure, checking properties:", 
                                    Object.keys(chatResponse.response));
                                
                                const complexResponse = chatResponse.response;
                                
                                // Option 4.1: Blocks array
                                if (complexResponse.blocks && Array.isArray(complexResponse.blocks)) {
                                    console.log("Found blocks array with", complexResponse.blocks.length, "blocks");
                                    const textBlocks = complexResponse.blocks
                                        .filter((block: any) => block && block.block_type === 'text')
                                        .map((block: any) => block.text || '');
                                        
                                    console.log("Extracted text blocks:", textBlocks);
                                    responseText = textBlocks.join('\n\n');
                                } 
                                // Option 4.2: Content field
                                else if (complexResponse.content && typeof complexResponse.content === 'string') {
                                    console.log("Found content field");
                                    responseText = complexResponse.content;
                                }
                                // Option 4.3: Text field
                                else if (complexResponse.text && typeof complexResponse.text === 'string') {
                                    console.log("Found text field");
                                    responseText = complexResponse.text;
                                }
                                // Option 4.4: Message field
                                else if (complexResponse.message && typeof complexResponse.message === 'string') {
                                    console.log("Found message field");
                                    responseText = complexResponse.message;
                                }
                            }
                            
                            // Option 5: Top-level content property
                            if (!responseText && chatResponse.content && typeof chatResponse.content === 'string') {
                                console.log("Found top-level content field");
                                responseText = chatResponse.content;
                            }
                            
                            // If nothing else works, try to stringify the whole object
                            if (!responseText && typeof chatResponse === 'object') {
                                try {
                                    // If it's a complex object, try to extract meaningful text
                                    const stringified = JSON.stringify(chatResponse);
                                    if (stringified.length < 1000) { // Don't use if it's too large
                                        responseText = "Response: " + stringified;
                                    }
                                } catch (e) {
                                    console.error("Error stringifying response:", e);
                                }
                            }
                        }
                        
                        // Fallback if we couldn't extract response text
                        if (!responseText) {
                            console.warn("Could not extract text from response. Using default message.");
                            responseText = "I received a response but couldn't process it correctly. Please try again.";
                        }
                        
                        console.log("Final extracted response text:", responseText);
                        
                        // Create a new bot message with the AI response
                        await createMessage({
                            conversationId: variables.conversationId,
                            content: responseText,
                            isBot: true
                        });
                        
                        // Invalidate again to show the bot response
                        queryClient.invalidateQueries({
                            queryKey: ["messages", variables.conversationId]
                        });
                    } catch (error) {
                        console.error("Error getting AI response:", error);
                        
                        // Fallback to a simple error message if the API call fails
                        await createMessage({
                            conversationId: variables.conversationId,
                            content: "I'm sorry, I encountered an error processing your request. Please try again later.",
                            isBot: true
                        });
                        
                        queryClient.invalidateQueries({
                            queryKey: ["messages", variables.conversationId]
                        });
                    }
                }, 500); // Shorter delay for API-based responses
            }
        },
        onError: (error: Error) => {
            console.error("Error creating message:", error);
        }
    });
};