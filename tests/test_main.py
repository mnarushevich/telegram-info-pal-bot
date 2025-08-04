"""Tests for the main module."""

from unittest.mock import MagicMock, patch

from telegram_bot.main import main


class TestMain:
    """Test cases for the main function."""

    def test_main_polling_mode(self, mock_settings):
        """Test main function in polling mode."""
        mock_settings.webhook_url = None

        with (
            patch("telegram_bot.main.create_settings", return_value=mock_settings),
            patch("telegram_bot.main.create_bot") as mock_create_bot,
            patch("sys.exit") as mock_exit,
        ):

            mock_bot = MagicMock()
            mock_create_bot.return_value = mock_bot

            # Mock run_polling to raise KeyboardInterrupt to exit gracefully
            mock_bot.run_polling.side_effect = KeyboardInterrupt()

            main()

            mock_create_bot.assert_called_once_with(mock_settings)
            mock_bot.run_polling.assert_called_once()
            mock_exit.assert_called_once_with(0)

    def test_main_webhook_mode(self, mock_settings):
        """Test main function in webhook mode."""
        mock_settings.webhook_url = "https://example.com/webhook"
        mock_settings.webhook_port = 8443
        mock_settings.webhook_listen = "0.0.0.0"
        mock_settings.webhook_ssl_cert = "/path/to/cert.pem"
        mock_settings.webhook_ssl_priv = "/path/to/key.pem"

        with (
            patch("telegram_bot.main.create_settings", return_value=mock_settings),
            patch("telegram_bot.main.create_bot") as mock_create_bot,
            patch("sys.exit") as mock_exit,
        ):

            mock_bot = MagicMock()
            mock_create_bot.return_value = mock_bot

            # Mock run_webhook to raise KeyboardInterrupt to exit gracefully
            mock_bot.run_webhook.side_effect = KeyboardInterrupt()

            main()

            mock_create_bot.assert_called_once_with(mock_settings)
            mock_bot.run_webhook.assert_called_once_with(
                webhook_url="https://example.com/webhook",
                port=8443,
                listen="0.0.0.0",
                cert="/path/to/cert.pem",
                key="/path/to/key.pem",
            )
            mock_exit.assert_called_once_with(0)

    def test_main_keyboard_interrupt(self, mock_settings):
        """Test main function handling KeyboardInterrupt."""
        with (
            patch("telegram_bot.main.create_settings", return_value=mock_settings),
            patch("telegram_bot.main.create_bot") as mock_create_bot,
            patch("sys.exit") as mock_exit,
        ):

            mock_bot = MagicMock()
            mock_create_bot.return_value = mock_bot
            mock_bot.run_polling.side_effect = KeyboardInterrupt()

            main()

            mock_exit.assert_called_once_with(0)

    def test_main_exception_handling(self, mock_settings):
        """Test main function handling unexpected exceptions."""
        with (
            patch("telegram_bot.main.create_settings", return_value=mock_settings),
            patch("telegram_bot.main.create_bot") as mock_create_bot,
            patch("sys.exit") as mock_exit,
        ):

            mock_bot = MagicMock()
            mock_create_bot.return_value = mock_bot
            mock_bot.run_polling.side_effect = Exception("Test error")

            main()

            mock_exit.assert_called_once_with(1)

    def test_main_logging_setup(self, mock_settings):
        """Test that main function sets up logging."""
        with (
            patch("telegram_bot.main.create_settings", return_value=mock_settings),
            patch("telegram_bot.main.create_bot") as mock_create_bot,
            patch("telegram_bot.config.Settings.setup_logging") as mock_setup_logging,
            patch("sys.exit"),
        ):

            mock_bot = MagicMock()
            mock_create_bot.return_value = mock_bot
            mock_bot.run_polling.side_effect = KeyboardInterrupt()

            main()

            mock_setup_logging.assert_called_once()

    def test_main_create_bot_failure(self, mock_settings):
        """Test main function when bot creation fails."""
        with (
            patch("telegram_bot.main.create_settings", return_value=mock_settings),
            patch("telegram_bot.main.create_bot") as mock_create_bot,
            patch("sys.exit") as mock_exit,
        ):

            mock_create_bot.side_effect = Exception("Failed to create bot")

            main()

            mock_exit.assert_called_once_with(1)
