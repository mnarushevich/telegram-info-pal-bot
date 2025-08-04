# Telegram Personal Support Bot 🤖

A simple Python Telegram bot that echoes messages with random emojis, built with modern Python practices and comprehensive testing.

## ✨ Features

- **Echo Messages**: Responds to text messages by echoing them back with random emojis
- **Non-text Support**: Handles photos, stickers, and other media with friendly responses
- **Command Support**: `/start` and `/help` commands for user interaction
- **Production Ready**: Supports both polling (development) and webhook (production) modes
- **Comprehensive Testing**: Full test suite with pytest
- **Modern Python**: Uses Python 3.12+ with type hints and modern async/await syntax
- **Configuration Management**: Environment-based configuration with validation
- **Logging**: Structured logging with configurable levels

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- [Task](https://taskfile.dev/) for task management
- A Telegram bot token from [@BotFather](https://t.me/botfather)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd telegram-personal-support-bot
   ```

2. **Install dependencies:**

   ```bash
   task install-dev
   ```

3. **Set up environment:**

   ```bash
   cp env.sample .env
   ```

   Edit `.env` and add your Telegram bot token:

   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. **Run the bot:**
   ```bash
   task run
   ```

## 🛠️ Development

### Available Tasks

Use [Task](https://taskfile.dev/) to run common development tasks:

```bash
# Install dependencies
task install-dev

# Format code
task format

# Run linting
task lint

# Fix linting issues automatically
task lint-fix

# Run tests
task test

# Run tests with coverage
task test-cov

# Run all quality checks
task check

# Run bot locally
task run

# Run bot in development mode (with debug logging)
task run-dev

# Clean temporary files
task clean
```

### Project Structure

```
telegram-personal-support-bot/
├── src/
│   └── telegram_bot/
│       ├── __init__.py          # Package initialization
│       ├── main.py              # Main entry point
│       ├── bot.py               # Core bot implementation
│       ├── config.py            # Configuration management
│       └── emojis.py            # Emoji utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── test_bot.py              # Bot functionality tests
│   ├── test_config.py           # Configuration tests
│   ├── test_emojis.py           # Emoji utilities tests
│   └── test_main.py             # Main module tests
├── pyproject.toml               # UV/Python configuration
├── Taskfile.yml                 # Task definitions
├── env.sample                   # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

### Code Quality

The project uses several tools to maintain code quality:

- **[Ruff](https://github.com/astral-sh/ruff)**: Fast Python linter and formatter
- **[MyPy](https://mypy.readthedocs.io/)**: Static type checking
- **[Black](https://black.readthedocs.io/)**: Code formatting
- **[isort](https://pycqa.github.io/isort/)**: Import sorting
- **[Pytest](https://pytest.org/)**: Testing framework with coverage

All tools are configured in `pyproject.toml` and can be run via the Taskfile.

## 🔧 Configuration

The bot uses environment variables for configuration. Copy `env.sample` to `.env` and customize:

### Required Settings

- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather

### Optional Settings

- `BOT_NAME`: Bot display name (default: "Personal Support Bot")
- `BOT_DESCRIPTION`: Bot description
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `DEBUG`: Enable debug mode (true/false)
- `ENVIRONMENT`: Environment (development/production)

### Webhook Settings (Production)

For production deployment with webhooks:

- `WEBHOOK_URL`: Your webhook URL
- `WEBHOOK_PORT`: Webhook port (default: 8443)
- `WEBHOOK_LISTEN`: Listen address (default: 0.0.0.0)
- `WEBHOOK_SSL_CERT`: Path to SSL certificate
- `WEBHOOK_SSL_PRIV`: Path to SSL private key

## 🧪 Testing

The project includes comprehensive tests covering:

- Configuration validation and loading
- Emoji utility functions
- Bot command handling
- Message processing
- Error handling
- Integration scenarios

Run tests with:

```bash
# Run all tests
task test

# Run with coverage report
task test-cov

# Run specific test file
uv run pytest tests/test_bot.py -v
```

## 📦 Deployment

### Development Mode (Polling)

For development, the bot runs in polling mode by default:

```bash
task run-dev
```

### Production Mode (Webhooks)

For production deployment, configure webhook settings in your environment:

```env
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_PORT=8443
ENVIRONMENT=production
```

The bot will automatically switch to webhook mode when `WEBHOOK_URL` is set.

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
RUN uv sync --no-dev

COPY src/ ./src/

# Run the bot
CMD ["uv", "run", "python", "-m", "telegram_bot.main"]
```

### Using UV for Deployment

The project is configured to work seamlessly with UV:

```bash
# Install for production
uv sync --no-dev

# Run the bot
uv run python -m telegram_bot.main
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`task check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Excellent Telegram Bot API wrapper
- [UV](https://github.com/astral-sh/uv) - Fast Python package manager
- [Pydantic](https://pydantic.dev/) - Data validation using Python type annotations
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter and formatter
