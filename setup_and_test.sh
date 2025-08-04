#!/bin/bash

# Telegram Personal Support Bot - Setup and Test Script
# This script demonstrates how to set up and test the project

set -e

echo "🤖 Telegram Personal Support Bot - Setup and Test"
echo "================================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if Task is installed
if ! command -v task &> /dev/null; then
    echo "❌ Task is not installed. Please install Task first:"
    echo "   https://taskfile.dev/installation/"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
uv sync --all-extras

echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from env.sample..."
    cp env.sample .env
    echo "⚠️  Please edit .env and add your TELEGRAM_BOT_TOKEN"
else
    echo "✅ .env file already exists"
fi

# Run linting and formatting
echo ""
echo "🔍 Running code quality checks..."
echo "  - Formatting code..."
uv run black src tests --quiet
uv run isort src tests --quiet

echo "  - Running linter..."
uv run ruff check src tests --quiet || true

echo "  - Running type checker..."
uv run mypy src --quiet || true

echo "✅ Code quality checks completed"

# Run tests
echo ""
echo "🧪 Running tests..."
uv run pytest tests/ -v --tb=short

echo ""
echo "📊 Running tests with coverage..."
uv run pytest tests/ --cov=src --cov-report=term-missing --quiet

echo ""
echo "🎉 Setup and testing completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your TELEGRAM_BOT_TOKEN"
echo "2. Run the bot: task run"
echo "3. Or use: uv run python -m telegram_bot.main"
echo ""
echo "For development: task run-dev"
echo "For all commands: task --list"