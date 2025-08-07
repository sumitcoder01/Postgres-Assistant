import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from a .env file into the system's environment
load_dotenv()

class Settings(BaseSettings):
    """
    Manages all application settings using Pydantic.
    It reads environment variables, validates their types, and provides
    a centralized, typed configuration object for the rest of the application.
    """
    # --- Database Configuration ---
    # This URI is passed to the MCP server.
    POSTGRES_URI: str

    # --- LLM Configuration ---
    LLM_PROVIDER: str = "openai"

    # --- API Keys ---
    # These are defined as optional because the application only requires one
    # to be present at runtime, depending on the chosen LLM_PROVIDER.
    # The logic in the llm_service will handle the validation.
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    DEEPSEEK_API_KEY: str | None = os.getenv("DEEPSEEK_API_KEY")

    class Config:
        # Specifies the .env file to load variables from.
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # Allows Pydantic to be case-insensitive with environment variables.
        case_sensitive = False

settings = Settings()