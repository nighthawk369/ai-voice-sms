"""Application configuration and settings"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    APP_NAME: str = "AI Platform"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str

    # AWS / S3
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "dev"
    AWS_SECRET_ACCESS_KEY: str = "dev"
    S3_BUCKET_DOCUMENTS: str = "documents-dev"
    S3_BUCKET_RECORDINGS: str = "recordings-dev"
    S3_BUCKET_EXPORTS: str = "exports-dev"
    MINIO_ENDPOINT: str = "http://minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"

    # Authentication & Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # LLM Providers
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Google
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-2.0-flash-exp"

    # Local LLM
    LOCAL_LLM_ENDPOINT: str = "http://localhost:8000/v1"
    LOCAL_LLM_MODEL: str = "mistral"

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # Stripe
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Email
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@example.com"
    FROM_NAME: str = "AI Platform"

    # Feature Flags
    FEATURE_FLAG_VOICE_AI: bool = True
    FEATURE_FLAG_SMS_AI: bool = True
    FEATURE_FLAG_PRIVATE_AI: bool = True
    FEATURE_FLAG_WORKFLOWS: bool = False
    FEATURE_FLAG_ADVANCED_ANALYTICS: bool = False

    # Sentry
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
