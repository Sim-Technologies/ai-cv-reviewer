import os
from langchain_anthropic import ChatAnthropic

DEFAULT_MODEL = "claude-sonnet-4-20250514"

def get_chat_model(model: str = DEFAULT_MODEL) -> ChatAnthropic:
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
        get_chat_model()
        return True
    except Exception as e:
        print(f"API key validation failed: {e}")
        return False 