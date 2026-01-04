"""
Application Configuration

Loads settings from environment variables using Pydantic Settings.
Settings are loaded from /root/.claude/.env by default.
"""
from functools import lru_cache
from typing import Optional
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    Required settings will raise clear errors if missing.
    """

    # API Configuration
    api_version: str = Field(default="0.1.0", description="API version")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Enable debug mode")

    # CORS Origins (comma-separated)
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated)",
    )

    # Supabase Configuration (Required for database operations)
    supabase_url: Optional[str] = Field(default=None, description="Supabase project URL")
    supabase_anon_key: Optional[str] = Field(default=None, description="Supabase anon key")
    supabase_service_key: Optional[str] = Field(default=None, description="Supabase service key")

    # Neo4j Configuration (Required for knowledge graph)
    neo4j_uri: Optional[str] = Field(default=None, description="Neo4j bolt URI")
    neo4j_user: Optional[str] = Field(default=None, description="Neo4j username")
    neo4j_password: Optional[str] = Field(default=None, description="Neo4j password")

    # Firebase Configuration (Required for auth)
    firebase_project_id: Optional[str] = Field(default=None, description="Firebase project ID")

    # OpenAI Configuration (Required for embeddings)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")

    # Anthropic Configuration (Required for AI processing)
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")

    # ClickUp Configuration
    clickup_api_key: Optional[str] = Field(default=None, description="ClickUp API key")
    clickup_team_id: Optional[str] = Field(default=None, description="ClickUp team ID")
    clickup_webhook_secret: Optional[str] = Field(default=None, description="ClickUp webhook secret for signature verification")

    model_config = SettingsConfigDict(
        env_file="/root/flourisha/00_AI_Brain/.env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars not in schema
        case_sensitive=False,  # Allow SUPABASE_URL or supabase_url
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_required_for_feature(self, feature: str) -> None:
        """Validate that required settings are present for a feature.

        Raises ValueError with clear message if required settings are missing.
        """
        required_settings = {
            "database": ["supabase_url", "supabase_service_key"],
            "knowledge_graph": ["neo4j_uri", "neo4j_user", "neo4j_password"],
            "auth": ["firebase_project_id"],
            "embeddings": ["openai_api_key"],
            "ai_processing": ["anthropic_api_key"],
        }

        if feature not in required_settings:
            return

        missing = []
        for setting in required_settings[feature]:
            if getattr(self, setting, None) is None:
                missing.append(setting.upper())

        if missing:
            raise ValueError(
                f"Missing required settings for {feature}: {', '.join(missing)}. "
                f"Please set these in /root/.claude/.env"
            )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Usage as dependency:
        @app.get("/example")
        async def example(settings: Settings = Depends(get_settings)):
            return {"debug": settings.debug}

    Returns:
        Cached Settings instance
    """
    return Settings()


def validate_startup_config() -> None:
    """Validate configuration at startup.

    Called during app startup to ensure critical config is present.
    Raises clear errors if required settings are missing.
    """
    settings = get_settings()

    # Log configuration status (not values for security)
    config_status = {
        "supabase": bool(settings.supabase_url),
        "neo4j": bool(settings.neo4j_uri),
        "firebase": bool(settings.firebase_project_id),
        "openai": bool(settings.openai_api_key),
        "anthropic": bool(settings.anthropic_api_key),
        "clickup": bool(settings.clickup_api_key),
        "clickup_webhook": bool(settings.clickup_webhook_secret),
    }

    print(f"Configuration loaded: {config_status}")

    # Don't fail startup for missing config - features will validate when needed
    return settings
