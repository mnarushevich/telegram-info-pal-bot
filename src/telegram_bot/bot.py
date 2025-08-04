"""Main Telegram bot implementation."""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import create_settings
from config.settings import Settings

from .emojis import add_random_emoji_to_text

logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot class."""

    def __init__(self, token: str) -> None:
        """Initialize the bot with the given token.

        Args:
            token: Telegram bot token from @BotFather.
        """
        self.token = token
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up bot command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Message handler for text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
        )

        # Handler for other types of messages (photos, stickers, etc.)
        self.application.add_handler(
            MessageHandler(
                ~filters.TEXT & ~filters.COMMAND, self.handle_non_text_message
            )
        )

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /start command.

        Args:
            update: Incoming update from Telegram.
            context: Context passed by the telegram.ext framework.
        """
        settings = create_settings()
        if update.effective_user:
            user_name = update.effective_user.first_name or "there"
            welcome_message = (
                f"Hello {user_name}! 👋\n\n"
                f"I'm {settings.bot_name}. {settings.bot_description}\n\n"
                "Just send me any message and I'll echo it back with a random emoji! 😊"
            )
        else:
            welcome_message = (
                f"Hello! 👋\n\n"
                f"I'm {settings.bot_name}. {settings.bot_description}\n\n"
                "Just send me any message and I'll echo it back with a random emoji! 😊"
            )

        if update.message:
            await update.message.reply_text(welcome_message)

        logger.info(
            "User %s started the bot",
            update.effective_user.id if update.effective_user else "Unknown",
        )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /help command.

        Args:
            update: Incoming update from Telegram.
            context: Context passed by the telegram.ext framework.
        """
        help_message = (
            "🤖 Bot Commands:\n\n"
            "/start - Start the bot and get a welcome message\n"
            "/help - Show this help message\n\n"
            "📝 How to use:\n"
            "Simply send me any text message and I'll echo it back with a random emoji!\n\n"
            "✨ Features:\n"
            "• Echoes your text messages with random emojis\n"
            "• Responds to photos, stickers, and other media\n"
            "• Simple and fun interaction\n\n"
            "Have fun chatting! 🎉"
        )

        if update.message:
            await update.message.reply_text(help_message)

    async def echo_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Echo the user's text message with a random emoji.

        Args:
            update: Incoming update from Telegram.
            context: Context passed by the telegram.ext framework.
        """
        if update.message and update.message.text:
            original_text = update.message.text
            response_text = add_random_emoji_to_text(original_text)

            await update.message.reply_text(response_text)

            logger.info(
                "Echoed message from user %s: %s -> %s",
                update.effective_user.id if update.effective_user else "Unknown",
                original_text,
                response_text,
            )

    async def handle_non_text_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle non-text messages (photos, stickers, etc.).

        Args:
            update: Incoming update from Telegram.
            context: Context passed by the telegram.ext framework.
        """
        if update.message:
            # For non-text messages, send a friendly response with emoji
            response_text = add_random_emoji_to_text("Nice!")
            await update.message.reply_text(response_text)

            logger.info(
                "Received non-text message from user %s",
                update.effective_user.id if update.effective_user else "Unknown",
            )

    async def error_handler(
        self, update: object, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle errors that occur during bot operation.

        Args:
            update: The update that caused the error.
            context: Context passed by the telegram.ext framework.
        """
        logger.error("Exception while handling an update:", exc_info=context.error)

    def run_polling(self) -> None:
        """Run the bot using polling (for development)."""
        logger.info("Starting bot in polling mode...")

        # Add error handler
        self.application.add_error_handler(self.error_handler)

        # Start the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def run_webhook(
        self,
        webhook_url: str,
        port: int = 8443,
        listen: str = "0.0.0.0",
        cert: str | None = None,
        key: str | None = None,
    ) -> None:
        """Run the bot using webhooks (for production).

        Args:
            webhook_url: The webhook URL.
            port: Port to listen on.
            listen: IP address to listen on.
            cert: Path to SSL certificate file.
            key: Path to SSL private key file.
        """
        logger.info("Starting bot in webhook mode on %s:%s", listen, port)

        # Add error handler
        self.application.add_error_handler(self.error_handler)

        # Start the webhook
        self.application.run_webhook(
            listen=listen,
            port=port,
            webhook_url=webhook_url,
            cert=cert,
            key=key,
            allowed_updates=Update.ALL_TYPES,
        )


def create_bot(settings: Settings | None = None) -> TelegramBot:
    """Create and configure the Telegram bot.

    Args:
        settings: Optional settings instance. If not provided, creates a new one.

    Returns:
        Configured TelegramBot instance.
    """
    if settings is None:
        settings = create_settings()
    return TelegramBot(settings.telegram_bot_token)
