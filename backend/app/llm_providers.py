"""
LLM Provider Implementations for ConversationChatBot
Supports both OpenAI and Ollama integrations.
"""

from typing import Dict, Any, Optional, List, Union
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import LLM
from llama_index.core.settings import Settings
from app.config import local_settings
import os

def get_openai_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 512
) -> OpenAI:
    """
    Initialize an OpenAI LLM client.
    
    Args:
        model_name: The OpenAI model to use (defaults to the one in settings)
        temperature: Controls randomness (0 = deterministic, 1 = creative)
        max_tokens: Maximum tokens in the response
        
    Returns:
        OpenAI LLM instance
    """
    model = model_name or local_settings.OPENAI_MODEL
    return OpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

def get_ollama_llm(
    model_name: str = "deepseek-coder:latest",
    base_url: Optional[str] = None,
    temperature: float = 0.0,
    context_window: int = 4096,
    max_tokens: int = 512
) -> Ollama:
    """
    Initialize an Ollama LLM client.
    
    Args:
        model_name: The Ollama model to use (e.g. "deepseek-coder:latest")
        base_url: The URL of the Ollama server (defaults to http://localhost:11434)
        temperature: Controls randomness (0 = deterministic, 1 = creative)
        context_window: Size of the context window
        max_tokens: Maximum tokens in the response
    
    Returns:
        Ollama LLM instance
    """
    # Use environment variable if set, otherwise use default localhost
    base_url = base_url or local_settings.OLLAMA_BASE_URL

    return Ollama(
        model=model_name,
        base_url=base_url,
        temperature=temperature,
        context_window=context_window,
        max_tokens=max_tokens,
        request_timeout=120.0  # Longer timeout for larger models
    )

def get_llm(provider: str = "openai", **kwargs) -> LLM:
    """
    Factory function to get the appropriate LLM based on provider.
    
    Args:
        provider: The LLM provider to use ("openai" or "ollama")
        **kwargs: Additional arguments to pass to the LLM constructor
        
    Returns:
        LLM instance
    
    Raises:
        ValueError: If provider is not supported
    """
    if provider.lower() == "openai":
        # Filter out kwargs that are not supported by OpenAI
        openai_kwargs = {k: v for k, v in kwargs.items() 
                         if k in ['model_name', 'temperature', 'max_tokens']}
        return get_openai_llm(**openai_kwargs)
    elif provider.lower() == "ollama":
        return get_ollama_llm(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
