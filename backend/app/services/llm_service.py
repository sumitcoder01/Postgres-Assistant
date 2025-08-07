# postgres-assistant/backend/app/services/llm_service.py

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from app.core.settings import settings

def get_llm() -> BaseChatModel:
    """
    Factory function to get an instance of the configured LLM provider.

    This function reads the LLM_PROVIDER from the application settings and
    initializes the corresponding LangChain chat model client. It centralizes
    the LLM selection logic, making the rest of the application independent
    of the specific LLM being used.

    Raises:
        ValueError: If the configured LLM_PROVIDER is not supported or if the
                    required API key for the selected provider is not set.

    Returns:
        An instance of a class that inherits from BaseChatModel, configured
        for streaming and ready to be used by the agent.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("LLM_PROVIDER is 'openai', but OPENAI_API_KEY is not set.")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            model="gpt-4o", 
            temperature=0, 
            streaming=True
        )
    
    elif provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("LLM_PROVIDER is 'gemini', but GEMINI_API_KEY is not set.")
        return ChatGoogleGenerativeAI(
            google_api_key=settings.GEMINI_API_KEY, 
            model="gemini-1.5-flash",
            temperature=0,
            # streaming is enabled by default in the underlying client
        )
    
    elif provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("LLM_PROVIDER is 'anthropic', but ANTHROPIC_API_KEY is not set.")
        return ChatAnthropic(
            api_key=settings.ANTHROPIC_API_KEY, 
            model="claude-3-5-sonnet-20240620", 
            temperature=0, 
            streaming=True
        )
        
    elif provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("LLM_PROVIDER is 'groq', but GROQ_API_KEY is not set.")
        return ChatGroq(
            api_key=settings.GROQ_API_KEY, 
            model="llama3-70b-8192", 
            temperature=0, 
            streaming=True
        )
        
    elif provider == "deepseek":
        # DeepSeek uses an OpenAI-compatible API structure.
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("LLM_PROVIDER is 'deepseek', but DEEPSEEK_API_KEY is not set.")
        return ChatOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            temperature=0,
            streaming=True
        )
        
    else:
        raise ValueError(f"Unsupported LLM provider: '{settings.LLM_PROVIDER}'. "
                         f"Supported values are: 'openai', 'gemini', 'anthropic', 'groq', 'deepseek'.")