"""Main Telegram bot implementation."""

import logging
import os
import uuid

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
from .gemini import GeminiClient

logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram bot class."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the bot with the given settings.

        Args:
            settings: Settings instance.
        """
        self.settings = settings
        self.application = Application.builder().token(settings.telegram_bot_token).build()

        # Initialize Gemini client only if API key is provided
        try:
            self.gemini_client = GeminiClient(settings.gemini_api_key)
        except ValueError as e:
            logger.warning("Gemini client not initialized: %s", e)
            self.gemini_client = None

        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up bot command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("emoji", self.emoji_command))
        self.application.add_handler(CommandHandler("image", self.image_command))

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
            "/emoji - Send message with random emoji\n"
            "/image - Generate an image from a text prompt\n\n"
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

    async def emoji_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
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

    async def image_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle the /image command.

        Args:
            update: Incoming update from Telegram.
            context: Context passed by the telegram.ext framework.
        """
        if update.message and update.message.text:
            original_text = update.message.text
            user_id = update.effective_user.id if update.effective_user else "Unknown"
            filename = f"{user_id}_{uuid.uuid4()}.png"
            success = await self._generate_image(prompt=original_text, update=update, filename=filename)

            if success:
                # Reply with the generated image
                try:
                    with open(filename, 'rb') as photo:
                        await update.message.reply_photo(photo=photo, caption=f"Generated image for: {original_text}")
                    logger.info(
                        "Image sent to user %s",
                        update.effective_user.id if update.effective_user else "Unknown",
                    )

                    #TODO: Remove this after switching to S3 storage
                    # Clean up the temporary image file
                    try:
                        os.remove(filename)
                        logger.info("Temporary image file %s removed", filename)
                    except OSError as cleanup_error:
                        logger.warning("Failed to remove temporary file %s: %s", filename, cleanup_error)

                except Exception as e:
                    logger.error("Failed to send image: %s", e)
                    await update.message.reply_text("❌ Failed to send the generated image.")

                    # Try to clean up the file even if sending failed
                    try:
                        os.remove(filename)
                    except OSError:
                        pass  # Ignore cleanup errors if sending already failed
            else:
                logger.info(
                    "Image generation failed for user %s",
                    update.effective_user.id if update.effective_user else "Unknown",
                )

    async def echo_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if update.message and update.message.text:
            original_text = update.message.text
            await update.message.reply_text("I can't process text messages yet.")

            logger.info(
                "Received text message from user %s",
                update.effective_user.id if update.effective_user else "Unknown",
                original_text,
            )

    async def handle_non_text_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if update.message:
            original_text = update.message.text
            await update.message.reply_text("I can't process non-text messages yet.")

            logger.info(
                "Received non-text message from user %s",
                update.effective_user.id if update.effective_user else "Unknown",
                original_text,
            )


    async def _generate_image(self, prompt: str, update: Update, filename: str) -> bool:
        """Generate an image using Gemini API.

        Args:
            prompt: The prompt to generate the image.
            update: Telegram update object.
            filename: The filename to save the image to.

        Returns:
            bool: True if image generation was successful, False otherwise.
        """
        if self.gemini_client is None:
            logger.error("Gemini client not available - API key not configured")
            if update.message:
                await update.message.reply_text(
                    "❌ Image generation is not available. Gemini API key is not configured."
                )
            return False

        try:
            success = await self.gemini_client.generate_content(prompt, filename=filename)
            if not success:
                if update.message:
                    await update.message.reply_text(
                        "❌ Failed to generate image. Please try again later."
                    )
            return success
        except Exception as e:
            logger.error("Failed to generate image: %s", e)
            if update.message:
                await update.message.reply_text(
                    "❌ Failed to generate image. Please try again later."
                )
            return False

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
    return TelegramBot(settings=settings)
