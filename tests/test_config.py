"""Tests for configuration management."""

import logging
import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from config import Settings


class TestSettings:
    """Test cases for the Settings class."""

    def test_default_settings(self):
        """Test default settings creation."""
        # Create isolated environment for this test
        isolated_env = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            # Explicitly set defaults to override any auto-use fixture values
            "LOG_LEVEL": "INFO",
            "DEBUG": "false",
            "ENVIRONMENT": "production",
        }
        with patch.dict(os.environ, isolated_env, clear=True):
            settings = Settings()

            assert settings.telegram_bot_token == "test_token"
            assert settings.bot_name == "Personal Support Bot"
            assert (
                settings.bot_description
                == "A simple bot that echoes messages with random emojis"
            )
            assert settings.log_level == "INFO"
            assert settings.debug is False
            assert settings.environment == "production"

    def test_custom_settings(self):
        """Test custom settings from environment variables."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "custom_token",
            "BOT_NAME": "Custom Bot",
            "BOT_DESCRIPTION": "Custom description",
            "LOG_LEVEL": "DEBUG",
            "DEBUG": "true",
            "ENVIRONMENT": "development",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert settings.telegram_bot_token == "custom_token"
            assert settings.bot_name == "Custom Bot"
            assert settings.bot_description == "Custom description"
            assert settings.log_level == "DEBUG"
            assert settings.debug is True
            assert settings.environment == "development"

    def test_missing_required_token(self):
        """Test that missing token raises validation error."""
        # Test by creating Settings with explicit _env_file=None to bypass .env loading
        with patch.dict(os.environ, {}, clear=True):
            # Create Settings class that doesn't load any .env file
            class TestSettings(Settings):
                model_config = Settings.model_config.copy()
                model_config.update({"env_file": None})

            with pytest.raises(ValidationError) as exc_info:
                TestSettings()

            assert "telegram_bot_token" in str(exc_info.value)

    def test_invalid_log_level(self):
        """Test validation of log level."""
        with patch.dict(
            os.environ,
            {"TELEGRAM_BOT_TOKEN": "test_token", "LOG_LEVEL": "INVALID_LEVEL"},
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_invalid_environment(self):
        """Test validation of environment."""
        with patch.dict(
            os.environ,
            {"TELEGRAM_BOT_TOKEN": "test_token", "ENVIRONMENT": "invalid_env"},
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_webhook_settings(self):
        """Test webhook configuration."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "WEBHOOK_URL": "https://example.com/webhook",
            "WEBHOOK_PORT": "8443",
            "WEBHOOK_LISTEN": "127.0.0.1",
            "WEBHOOK_SSL_CERT": "/path/to/cert.pem",
            "WEBHOOK_SSL_PRIV": "/path/to/key.pem",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            assert settings.webhook_url == "https://example.com/webhook"
            assert settings.webhook_port == 8443
            assert settings.webhook_listen == "127.0.0.1"
            assert settings.webhook_ssl_cert == "/path/to/cert.pem"
            assert settings.webhook_ssl_priv == "/path/to/key.pem"

    def test_is_development_property(self):
        """Test the is_development property."""
        # Test production environment
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "ENVIRONMENT": "production",
                "DEBUG": "false",
            },
        ):
            settings = Settings()
            assert settings.is_development is False

        # Test development environment
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "ENVIRONMENT": "development",
                "DEBUG": "false",
            },
        ):
            settings = Settings()
            assert settings.is_development is True

        # Test debug mode
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "ENVIRONMENT": "production",
                "DEBUG": "true",
            },
        ):
            settings = Settings()
            assert settings.is_development is True

    def test_setup_logging(self):
        """Test logging setup."""
        with patch.dict(
            os.environ, {"TELEGRAM_BOT_TOKEN": "test_token", "LOG_LEVEL": "WARNING"}
        ):
            settings = Settings()

            # Mock the logging configuration
            with patch("logging.basicConfig") as mock_basic_config:
                settings.setup_logging()

                mock_basic_config.assert_called_once_with(
                    level=logging.WARNING, format=settings.log_format, force=True
                )

    def test_setup_logging_development_vs_production(self):
        """Test different logging setups for dev vs prod."""
        # Test production logging (should reduce noise)
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "test_token",
                "ENVIRONMENT": "production",
                "DEBUG": "false",
            },
        ):
            settings = Settings()

            with patch("logging.getLogger") as mock_get_logger:
                settings.setup_logging()

                # Should set WARNING level for noisy libraries
                assert mock_get_logger.call_count >= 2

        # Test development logging (should allow more verbose logging)
        with patch.dict(
            os.environ,
            {"TELEGRAM_BOT_TOKEN": "test_token", "ENVIRONMENT": "development"},
        ):
            settings = Settings()

            with patch("logging.getLogger") as mock_get_logger:
                settings.setup_logging()

                # Should not modify library log levels in development
                # (the method only sets WARNING for production)
