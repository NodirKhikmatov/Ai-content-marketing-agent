"""Application configuration loaded from environment variables."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Content Marketing Agent API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_secret_key: str = ""
    supabase_jwt_secret: str = ""

    # AI (required from Step 6 onward)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    # Route all pipeline tasks through Gemini (useful for free-tier dev).
    ai_prefer_gemini: bool = False
    # Return canned responses instead of calling real providers (offline dev/testing).
    ai_mock_mode: bool = False

    # AI models — overridable so model retirements don't require a code change.
    anthropic_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    openai_model_mini: str = "gpt-4o-mini"
    gemini_model: str = "gemini-flash-latest"

    # Redis
    redis_url: str = "redis://localhost:6379"
    # Run analyses through the durable arq worker instead of in-process BackgroundTasks.
    use_worker_queue: bool = False

    # CORS — comma-separated or JSON list
    cors_origins: list[str] = ["http://localhost:3000"]

    # Crawler
    max_crawl_pages: int = 10
    crawl_timeout_seconds: int = 30

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                import json
                return json.loads(value)
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value  # type: ignore[return-value]

    @property
    def supabase_api_key(self) -> str:
        """Server-side Supabase key: prefer new secret key, fall back to legacy service_role."""
        return self.supabase_secret_key or self.supabase_service_role_key

    @property
    def supabase_jwt_issuer(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1"

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_api_key)

    @property
    def is_auth_configured(self) -> bool:
        return bool(self.supabase_jwt_secret)

    @property
    def can_validate_jwt(self) -> bool:
        """JWKS validation works with SUPABASE_URL; legacy needs JWT secret."""
        return bool(self.supabase_url or self.supabase_jwt_secret)

    @property
    def is_openai_configured(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def is_anthropic_configured(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def is_ai_configured(self) -> bool:
        return (
            self.is_openai_configured
            or self.is_anthropic_configured
            or self.is_gemini_configured
        )


settings = Settings()
