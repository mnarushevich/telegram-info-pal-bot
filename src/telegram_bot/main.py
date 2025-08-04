"""Main entry point for the Telegram bot."""

import logging
import sys

from config import create_settings

from .bot import create_bot


def main() -> None:
    """Main function to run the Telegram bot."""
    # Create settings instance
    settings = create_settings()

    # Setup logging
    settings.setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting %s v%s", settings.bot_name, "0.1.0")
    logger.info("Environment: %s", settings.environment)
    logger.info("Debug mode: %s", settings.debug)

    try:
        # Create the bot
        bot = create_bot(settings)

        # Run the bot based on configuration
        if settings.webhook_url:
            logger.info("Running bot in webhook mode")
            bot.run_webhook(
                webhook_url=settings.webhook_url,
                port=settings.webhook_port,
                listen=settings.webhook_listen,
                cert=settings.webhook_ssl_cert,
                key=settings.webhook_ssl_priv,
            )
        else:
            logger.info("Running bot in polling mode")
            bot.run_polling()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal error occurred: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
