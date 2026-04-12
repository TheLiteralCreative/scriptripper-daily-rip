from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "ScriptRipper"
    APP_VERSION: str = "0.2.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    # Render internal URL (used in production). For local Alembic runs, set
    # DATABASE_URL_EXTERNAL in your local .env to the Render external URL.
    DATABASE_URL: str
    DATABASE_URL_EXTERNAL: str = ""  # local dev only — NOT committed

    # Redis (Render internal URL in prod)
    REDIS_URL: str

    # Auth / JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAGIC_LINK_EXPIRE_MINUTES: int = 15

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str  # NOTE: malformed in legacy env — fix before deploying

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8000"

    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    # LLM
    DEFAULT_LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Transcription (Groq Whisper)
    GROQ_API_KEY: str = ""  # NOT in legacy env — add to Render env vars

    # Email (PurelyMail)
    FROM_EMAIL: str = "noreply@scriptripper.com"
    PURELYMAIL_SMTP_HOST: str = "smtp.purelymail.com"
    PURELYMAIL_SMTP_PORT: int = 587
    PURELYMAIL_API_TOKEN: str = ""

    # Storage (Cloudflare R2 — S3-compatible)
    S3_BUCKET_NAME: str = "scriptripper-artifacts"
    S3_REGION: str = "auto"
    R2_ACCESS_KEY_ID: str = ""       # NOT in legacy env — add to Render env vars
    R2_SECRET_ACCESS_KEY: str = ""   # NOT in legacy env — add to Render env vars
    R2_ENDPOINT_URL: str = ""        # e.g. https://<account_id>.r2.cloudflarestorage.com

    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # Payments
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_PRO_PRICE_ID: str = ""
    STRIPE_SUCCESS_URL: str = "https://scriptripper.com/success"
    STRIPE_CANCEL_URL: str = "https://scriptripper.com/pricing"

    # Cron
    CRON_SECRET_KEY: str = ""  # NOT in legacy env — generate and add to Render env vars

    # Limits
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_TRANSCRIPT_LENGTH: int = 500000
    RATE_LIMIT_PER_MINUTE: int = 60

    @computed_field
    @property
    def database_async_url(self) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @computed_field
    @property
    def alembic_url(self) -> str:
        """Sync URL for Alembic migrations. Uses external URL if set (local dev)."""
        url = self.DATABASE_URL_EXTERNAL or self.DATABASE_URL
        # Strip any +asyncpg driver suffix for sync Alembic use
        return url.replace("+asyncpg", "")


settings = Settings()
