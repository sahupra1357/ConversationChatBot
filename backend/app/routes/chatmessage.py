from fastapi import Form, Body
from llama_index.core.settings import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.prompts import PromptTemplate
import os
from app.config import local_settings
from llama_index.core.agent.workflow import ReActAgent
from app.arxiv_rag import get_lazy_load_and_query
from app.llm_providers import get_llm
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    message_history: Optional[List[Dict[str, Any]]] = None


# Initialize LLM based on configuration
llm = get_llm(
    provider=local_settings.LLM_PROVIDER,
    model_name=local_settings.OLLAMA_MODEL if local_settings.LLM_PROVIDER.lower() == "ollama" else local_settings.OPENAI_MODEL,
    temperature=local_settings.LLM_TEMPERATURE,
    max_tokens=local_settings.LLM_MAX_TOKENS,
    base_url=local_settings.OLLAMA_BASE_URL if local_settings.LLM_PROVIDER.lower() == "ollama" else None,
    context_window=local_settings.LLM_CONTEXT_WINDOW if local_settings.LLM_PROVIDER.lower() == "ollama" else None
)

# Configure LlamaIndex settings
Settings.llm = llm
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
Settings.num_output = local_settings.LLM_MAX_TOKENS
Settings.context_window = local_settings.LLM_CONTEXT_WINDOW

def read_prompt_file(file_path):
    """Read the system prompt from a file."""
    with open(file_path, 'r') as file:
        return file.read().strip()


lazy_load_and_query = get_lazy_load_and_query(llm=llm)
agent = ReActAgent(llm=llm, 
                   tools=[lazy_load_and_query],
                   verbose=True,)

system_prompt = read_prompt_file("app/system_prompt.txt")
agent.update_prompts({"react_header": PromptTemplate(system_prompt)})

router = APIRouter(tags=["chat"])

@router.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """
    Process a chat request with JSON data.
    Can receive conversation history for context.
    """
    print(f"Received chat request: {chat_request}")
    
    # Extract the message
    user_message = chat_request.message
    
    # Include conversation history if provided
    context = ""
    if chat_request.message_history:
        # Format message history as context
        for msg in chat_request.message_history:
            sender = "User" if not msg.get("isBot", False) else "Assistant"
            context += f"{sender}: {msg.get('content', '')}\n"
        
        if context:
            user_message = f"[Previous conversation:\n{context}]\n\nCurrent message: {user_message}"
    
    print(f"Processed user message: {user_message}")
    
    try:
        # Get response from agent
        response = await agent.run(user_message)
        #print(f"Agent response: {response[:100]}...")
        # print(f"Agent response: is back...", response)
        print(f"Agent response: is back...")
    except Exception as e:
        error_msg = str(e)
        print(f"Error in agent.run: {error_msg}")
        
        # More detailed error handling with specific messages
        if "Failed to fetch from arXiv" in error_msg:
            if "503" in error_msg:
                response = ("I'm having trouble connecting to the arXiv research database at the moment. "
                          "The server is temporarily unavailable (HTTP 503), which usually indicates "
                          "either maintenance or high traffic. Please try again in a few minutes. "
                          "In the meantime, I can still help answer your question based on my general knowledge.")
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                response = ("I've reached the rate limit for arXiv's API. "
                          "This happens when there are many research requests in a short period. "
                          "Please try again in a few minutes. "
                          "I can still help with questions that don't require the latest research papers.")
            elif "timeout" in error_msg.lower():
                response = ("The connection to arXiv's research database timed out. "
                          "This might be due to network issues or high server load. "
                          "Please try again shortly. "
                          "In the meantime, I can help with questions based on my general knowledge.")
            else:
                response = ("I'm having trouble connecting to the arXiv research database at the moment. "
                          "This could be due to network issues or rate limiting. "
                          "I can still help answer your question based on my general knowledge. "
                          "What would you like to know?")
        elif "vector store" in error_msg.lower() or "qdrant" in error_msg.lower():
            response = ("I'm experiencing an issue with my research database. "
                      "This is likely a temporary problem with how I store and retrieve research information. "
                      "Let me try to answer based on my general knowledge instead.")
        else:
            response = (f"I encountered an error while processing your request. "
                      f"Error details: {error_msg}. "
                      f"Please try again with a different question.")
    
    return {"response": response, "conversation_id": chat_request.conversation_id}
