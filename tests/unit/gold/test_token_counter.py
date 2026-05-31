"""Tests for TokenCounter service."""

from unittest.mock import MagicMock, patch

from formaforge.gold.token_counter import TokenCounter

_SAMPLE_TEXT = "Hello world, this is a test sentence with some words."


def test_generic_returns_positive() -> None:
    assert TokenCounter().count(_SAMPLE_TEXT, "generic") > 0


def test_generic_byte_heuristic() -> None:
    text = "a" * 400
    result = TokenCounter().count(text, "generic")
    assert result == 100


def test_small_uses_heuristic() -> None:
    text = "a" * 400
    assert TokenCounter().count(text, "small") == 100


def test_frontier_uses_heuristic() -> None:
    text = "a" * 400
    assert TokenCounter().count(text, "frontier") == 100


def test_gemini_uses_byte3_heuristic() -> None:
    text = "a" * 300
    result = TokenCounter().count(text, "gemini")
    assert result == 100


def test_claude_uses_heuristic() -> None:
    text = "a" * 400
    result = TokenCounter().count(text, "claude")
    assert result == 100


def test_gpt4_uses_tiktoken_when_available() -> None:
    mock_enc = MagicMock()
    mock_enc.encode.return_value = list(range(12))
    with patch("formaforge.gold.token_counter._get_tiktoken_encoder", return_value=mock_enc):
        result = TokenCounter().count(_SAMPLE_TEXT, "gpt4")
    assert result == 12
    mock_enc.encode.assert_called_once_with(_SAMPLE_TEXT)


def test_gpt4_falls_back_when_tiktoken_missing() -> None:
    with patch("formaforge.gold.token_counter._get_tiktoken_encoder", return_value=None):
        text = "a" * 400
        result = TokenCounter().count(text, "gpt4")
    assert result == 100


def test_empty_text_returns_at_least_one() -> None:
    assert TokenCounter().count("", "generic") >= 1
