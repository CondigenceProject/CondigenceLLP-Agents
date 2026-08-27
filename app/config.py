import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Condigence AI Operations System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    SECRET_KEY: str = "condigence_super_secret_dev_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # LLM & Observability
    LLM_PROVIDER: str = "openai"  # "openai" | "groq" | "gemini"
    OPENAI_API_KEY: Optional[str] = "mock_key"
    OPENAI_MODEL: str = "gpt-4o"
    
    # Groq Cloud (Free high-speed testing)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    
    # Google Gemini (Free generous quota via AI Studio)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-flash-latest"

    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "condigence-agentic-ops"

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "condigence_ops"

    # Redis (Caching, Locking & Ephemeral State)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Apache Kafka (Durable Event Bus & Message Streaming)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_ENABLE: bool = True
    KAFKA_TOPIC_AGENT_TASKS: str = "condigence.agent.tasks"
    KAFKA_TOPIC_AUDIT_LOGS: str = "condigence.audit.logs"
    KAFKA_TOPIC_APPROVALS: str = "condigence.approvals"

    # Pinecone Vector DB (SOP / Policy RAG)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "condigence-sop-index"

    # Zoho Books & CRM
    ZOHO_CLIENT_ID: Optional[str] = None
    ZOHO_CLIENT_SECRET: Optional[str] = None
    ZOHO_REFRESH_TOKEN: Optional[str] = None
    ZOHO_ORG_ID: Optional[str] = None

    # Notion
    NOTION_API_KEY: Optional[str] = None
    NOTION_TASK_DB_ID: Optional[str] = None

    # Email & WhatsApp
    GMAIL_CREDENTIALS_JSON_PATH: Optional[str] = None
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None

    # n8n Automation Engine
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
