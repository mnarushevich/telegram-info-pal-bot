"""Tests for the main bot functionality."""

from unittest.mock import MagicMock, patch

import pytest
from telegram import Update

from telegram_bot.bot import TelegramBot, create_bot
from telegram_bot.emojis import EMOJI_LIST


class TestTelegramBot:
    """Test cases for the TelegramBot class."""

    @pytest.fixture
    def bot(self, mock_settings):
        """Fixture providing a TelegramBot instance with mocked settings."""
        return TelegramBot("test_token")

    def test_bot_initialization(self, mock_settings):
        """Test bot initialization."""
        bot = TelegramBot("test_token")

        assert bot.token == "test_token"
        assert bot.application is not None

    async def test_start_command_with_user(
        self, bot, mock_update, mock_context, mock_settings, mock_user_testuser
    ):
        """Test /start command with a user."""
        mock_update.effective_user = mock_user_testuser

        with patch("telegram_bot.bot.create_settings", return_value=mock_settings):
            await bot.start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Hello TestUser!" in call_args
        assert "Test Bot" in call_args

    async def test_start_command_without_user(
        self, bot, mock_update, mock_context, mock_settings
    ):
        """Test /start command without a user."""
        mock_update.effective_user = None

        with patch("telegram_bot.bot.create_settings", return_value=mock_settings):
            await bot.start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Hello!" in call_args

    async def test_help_command(self, bot, mock_update, mock_context):
        """Test /help command."""
        await bot.help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Bot Commands:" in call_args
        assert "/start" in call_args
        assert "/help" in call_args

    async def test_echo_message(self, bot, mock_update, mock_context):
        """Test echoing a text message."""
        original_text = "Hello, bot!"
        mock_update.message.text = original_text

        await bot.echo_message(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        response_text = mock_update.message.reply_text.call_args[0][0]

        # Should start with original text
        assert response_text.startswith(original_text)
        # Should be longer (emoji added)
        assert len(response_text) > len(original_text)
        # Should contain an emoji
        emoji_part = response_text[len(original_text) :].strip()
        assert any(emoji in emoji_part for emoji in EMOJI_LIST)

    async def test_echo_message_no_text(self, bot, mock_update, mock_context):
        """Test echo_message when message has no text."""
        mock_update.message.text = None

        # Should not call reply_text if no text
        await bot.echo_message(mock_update, mock_context)

        mock_update.message.reply_text.assert_not_called()

    async def test_handle_non_text_message(self, bot, mock_update, mock_context):
        """Test handling non-text messages."""
        await bot.handle_non_text_message(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        response_text = mock_update.message.reply_text.call_args[0][0]

        # Should contain "Nice!" with emoji
        assert "Nice!" in response_text
        assert any(emoji in response_text for emoji in EMOJI_LIST)

    async def test_error_handler(self, bot, mock_context):
        """Test error handling."""
        mock_context.error = Exception("Test error")
        mock_update = MagicMock()

        with patch("telegram_bot.bot.logger") as mock_logger:
            await bot.error_handler(mock_update, mock_context)

            mock_logger.error.assert_called_once()

    def test_run_polling(self, bot):
        """Test running bot in polling mode."""
        with (
            patch("telegram.ext.Application.run_polling") as mock_run_polling,
            patch("telegram.ext.Application.add_error_handler") as mock_add_error,
        ):

            bot.run_polling()

            mock_add_error.assert_called_once()
            mock_run_polling.assert_called_once_with(allowed_updates=Update.ALL_TYPES)

    def test_run_webhook(self, bot):
        """Test running bot in webhook mode."""
        webhook_config = {
            "webhook_url": "https://example.com/webhook",
            "port": 8443,
            "listen": "0.0.0.0",
            "cert": "/path/to/cert.pem",
            "key": "/path/to/key.pem",
        }

        with (
            patch("telegram.ext.Application.run_webhook") as mock_run_webhook,
            patch("telegram.ext.Application.add_error_handler") as mock_add_error,
        ):

            bot.run_webhook(**webhook_config)

            mock_add_error.assert_called_once()
            mock_run_webhook.assert_called_once_with(
                listen="0.0.0.0",
                port=8443,
                webhook_url="https://example.com/webhook",
                cert="/path/to/cert.pem",
                key="/path/to/key.pem",
                allowed_updates=Update.ALL_TYPES,
            )


class TestCreateBot:
    """Test cases for the create_bot function."""

    def test_create_bot(self, mock_settings):
        """Test bot creation function."""
        bot = create_bot(mock_settings)

        assert isinstance(bot, TelegramBot)
        assert bot.token == mock_settings.telegram_bot_token

    def test_create_bot_uses_settings_token(self, mock_settings):
        """Test that create_bot uses token from settings."""
        expected_token = "test_token_from_settings"
        mock_settings.telegram_bot_token = expected_token

        bot = create_bot(mock_settings)

        assert bot.token == expected_token
