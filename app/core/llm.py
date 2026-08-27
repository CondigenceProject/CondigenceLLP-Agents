import logging
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from app.config import settings

logger = logging.getLogger("condigence.core.llm")


def get_llm(temperature: float = 0.2, streaming: bool = False) -> Optional[BaseChatModel]:
    """
    Factory to instantiate the configured LLM provider:
    - "openai": Standard OpenAI GPT-4o / GPT-4o-mini
    - "groq": Ultra high-speed open models (Llama 3.3 70B, Llama 3.1 8B, DeepSeek R1)
    - "gemini": Google Gemini 1.5 Flash / 2.0 Flash via OpenAI compatibility endpoint
    """
    provider = settings.LLM_PROVIDER.lower().strip()

    # Auto-detect if provider is default openai but groq or gemini key is provided
    if provider == "openai" and (not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "mock_key"):
        if settings.GROQ_API_KEY:
            provider = "groq"
        elif settings.GEMINI_API_KEY:
            provider = "gemini"

    logger.info(f"Initializing LLM client using provider: [{provider}]")

    try:
        if provider == "groq":
            api_key = settings.GROQ_API_KEY or "mock_key"
            return ChatOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key,
                model=settings.GROQ_MODEL,
                temperature=temperature,
                streaming=streaming
            )

        elif provider == "gemini":
            api_key = settings.GEMINI_API_KEY or "mock_key"
            return ChatOpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=api_key,
                model=settings.GEMINI_MODEL,
                temperature=temperature,
                streaming=streaming
            )

        else:
            # Default to OpenAI
            api_key = settings.OPENAI_API_KEY or "mock_key"
            return ChatOpenAI(
                api_key=api_key,
                model=settings.OPENAI_MODEL,
                temperature=temperature,
                streaming=streaming
            )

    except Exception as e:
        logger.warning(f"Could not initialize live LLM provider ({provider}): {e}. Falling back to default mock.")
        return None
