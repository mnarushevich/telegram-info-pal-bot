"""Configuration management for the Telegram bot."""

import logging
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(
        ...,
        description="Telegram bot token from @BotFather",
        min_length=1,
    )

    # Bot Settings
    bot_name: str = Field(
        default="Personal Support Bot",
        description="Name of the bot",
    )
    bot_description: str = Field(
        default="A simple bot that echoes messages with random emojis",
        description="Bot description",
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format",
    )

    # Development Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    environment: Literal["development", "production"] = Field(
        default="production",
        description="Application environment",
    )

    # Optional: Webhook settings (for production deployment)
    webhook_url: str | None = Field(
        default=None,
        description="Webhook URL for production deployment",
    )
    webhook_port: int = Field(
        default=8443,
        description="Webhook port",
        ge=1,
        le=65535,
    )
    webhook_listen: str = Field(
        default="0.0.0.0",
        description="Webhook listen address",
    )
    webhook_ssl_cert: str | None = Field(
        default=None,
        description="Path to SSL certificate file",
    )
    webhook_ssl_priv: str | None = Field(
        default=None,
        description="Path to SSL private key file",
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development" or self.debug

    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=self.log_format,
            force=True,
        )

        # Reduce noise from some libraries in production
        if not self.is_development:
            logging.getLogger("httpx").setLevel(logging.WARNING)
            logging.getLogger("telegram").setLevel(logging.WARNING)


# Global settings instance - instantiated only when module is not being imported for testing
def create_settings() -> Settings:
    """Create a new Settings instance."""
    return Settings()  # type: ignore[call-arg]


# Global settings instance (will be set in main.py or explicitly when needed)
settings: Settings | None = None