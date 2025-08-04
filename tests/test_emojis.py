"""Tests for emoji functionality."""

from telegram_bot.emojis import (
    EMOJI_LIST,
    add_random_emoji_to_text,
    get_random_emoji,
    get_random_emojis,
)


class TestEmojiUtils:
    """Test cases for emoji utility functions."""

    def test_emoji_list_not_empty(self):
        """Test that the emoji list is not empty."""
        assert len(EMOJI_LIST) > 0
        assert all(isinstance(emoji, str) for emoji in EMOJI_LIST)

    def test_get_random_emoji(self):
        """Test getting a random emoji."""
        emoji = get_random_emoji()

        assert isinstance(emoji, str)
        assert emoji in EMOJI_LIST
        assert len(emoji) > 0

    def test_get_random_emoji_variety(self):
        """Test that random emoji returns different emojis over multiple calls."""
        emojis = [get_random_emoji() for _ in range(100)]
        unique_emojis = set(emojis)

        # With a large enough list, we should get some variety
        # (though this could theoretically fail due to randomness)
        assert len(unique_emojis) > 1

    def test_get_random_emojis_single(self):
        """Test getting a single random emoji using get_random_emojis."""
        emojis = get_random_emojis(1)

        assert isinstance(emojis, list)
        assert len(emojis) == 1
        assert emojis[0] in EMOJI_LIST

    def test_get_random_emojis_multiple(self):
        """Test getting multiple random emojis."""
        count = 5
        emojis = get_random_emojis(count)

        assert isinstance(emojis, list)
        assert len(emojis) == count
        assert all(emoji in EMOJI_LIST for emoji in emojis)

    def test_get_random_emojis_zero(self):
        """Test getting zero emojis."""
        emojis = get_random_emojis(0)

        assert isinstance(emojis, list)
        assert len(emojis) == 0

    def test_add_random_emoji_to_text_normal(self):
        """Test adding emoji to normal text."""
        original_text = "Hello, world!"
        result = add_random_emoji_to_text(original_text)

        assert result.startswith(original_text)
        assert len(result) > len(original_text)
        assert " " in result  # Should have a space before emoji

        # Extract the emoji part
        emoji_part = result[len(original_text) :].strip()
        assert emoji_part in EMOJI_LIST

    def test_add_random_emoji_to_text_multiple(self):
        """Test adding multiple emojis to text."""
        original_text = "Hello, world!"
        emoji_count = 3
        result = add_random_emoji_to_text(original_text, emoji_count)

        assert result.startswith(original_text)
        assert len(result) > len(original_text)

        # Should have spaces separating emojis
        emoji_part = result[len(original_text) :].strip()
        emojis = emoji_part.split(" ")
        assert len(emojis) == emoji_count
        assert all(emoji in EMOJI_LIST for emoji in emojis)

    def test_add_random_emoji_to_empty_text(self):
        """Test adding emoji to empty text."""
        result = add_random_emoji_to_text("")

        assert result in EMOJI_LIST
        assert len(result) > 0

    def test_add_random_emoji_to_whitespace_text(self):
        """Test adding emoji to whitespace-only text."""
        result = add_random_emoji_to_text("   ")

        assert result in EMOJI_LIST
        assert len(result) > 0

    def test_add_random_emoji_preserves_text(self):
        """Test that original text is preserved exactly."""
        test_cases = [
            "Simple text",
            "Text with numbers 123",
            "Text with symbols !@#$%",
            "Text with\nnewlines",
            "Text with\ttabs",
            "Multiple    spaces",
        ]

        for original_text in test_cases:
            result = add_random_emoji_to_text(original_text)
            assert result.startswith(original_text.strip())

    def test_add_random_emoji_default_count(self):
        """Test that default emoji count is 1."""
        original_text = "Test message"
        result = add_random_emoji_to_text(original_text)

        # Should have exactly one emoji added
        emoji_part = result[len(original_text) :].strip()
        assert " " not in emoji_part  # No spaces means single emoji
        assert emoji_part in EMOJI_LIST

    def test_emoji_list_contains_valid_emojis(self):
        """Test that emoji list contains what appear to be valid emojis."""
        for emoji in EMOJI_LIST:
            # Basic checks for emoji-like strings
            assert isinstance(emoji, str)
            assert len(emoji) > 0
            # Most emojis are represented as multi-byte unicode
            assert len(emoji.encode("utf-8")) > len(emoji)
