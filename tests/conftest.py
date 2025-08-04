"""Pytest configuration and shared fixtures."""

import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import Bot, Message, Update, User
from telegram.ext import ContextTypes

from config import Settings


@pytest.fixture
def mock_settings():
    """Fixture providing mock settings for testing."""
    return Settings(
        telegram_bot_token="test_token_123",
        bot_name="Test Bot",
        bot_description="A test bot",
        log_level="INFO",
        debug=True,
        environment="development",
    )


@pytest.fixture
def mock_user():
    """Fixture providing a mock Telegram user."""
    return User(
        id=12345,
        first_name="Test",
        last_name="User",
        username="testuser",
        is_bot=False,
    )


@pytest.fixture
def mock_user_testuser():
    """Fixture providing a mock Telegram user with TestUser name."""
    return User(
        id=12345,
        first_name="TestUser",
        last_name="User",
        username="testuser",
        is_bot=False,
    )


@pytest.fixture
def mock_message(mock_user):
    """Fixture providing a mock Telegram message."""
    message = MagicMock(spec=Message)
    message.message_id = 1
    message.from_user = mock_user
    message.text = "Hello, bot!"
    message.reply_text = AsyncMock()
    return message


@pytest.fixture
def mock_update(mock_user, mock_message):
    """Fixture providing a mock Telegram update."""
    update = MagicMock(spec=Update)
    update.effective_user = mock_user
    update.message = mock_message
    return update


@pytest.fixture
def mock_context():
    """Fixture providing a mock context."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock(spec=Bot)
    return context


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Set test environment variables
    test_env = {
        "TELEGRAM_BOT_TOKEN": "test_token_123",
        "LOG_LEVEL": "DEBUG",
        "DEBUG": "true",
        "ENVIRONMENT": "development",
    }

    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    # Test environment is set up
    yield

    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value
