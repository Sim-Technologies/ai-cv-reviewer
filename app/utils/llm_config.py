import os
from typing import Optional
from anthropic import Anthropic
from langchain_anthropic import ChatAnthropic


def get_anthropic_client() -> Anthropic:
    """Get Anthropic client instance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    return Anthropic(api_key=api_key)


def get_chat_model(model: str = "claude-sonnet-4-20250514") -> ChatAnthropic:
    """Get LangChain ChatAnthropic model instance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    return ChatAnthropic(
        model=model,
        anthropic_api_key=api_key,
        temperature=0.1,
        max_tokens=4000
    )


def validate_api_key() -> bool:
    """Validate that the API key is set and working."""
    try:
        get_anthropic_client()
        return True
    except Exception as e:
        print(f"API key validation failed: {e}")
        return False 