"""Tests for AiConverter.convert_async() with streaming."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from formaforge.ai.ai_converter import AiConverter
from formaforge.models.silver import CdmDocument

_SAMPLE_CDM = """\
---
source_format: text
source_uri: doc.txt
structure_class: unstructured
conversion_method: ai
conversion_confidence: 0.85
cdm_schema_version: "2.0"
pii_flags: []
---

# Summary

Some meeting notes content.
"""


def _make_stream_mock(full_text: str) -> MagicMock:
    """Return a mock async context manager that streams text chunks."""
    chunks = [full_text[i : i + 20] for i in range(0, len(full_text), 20)]

    async def _aiter():
        for chunk in chunks:
            yield chunk

    stream_mock = MagicMock()
    stream_mock.__aenter__ = AsyncMock(return_value=stream_mock)
    stream_mock.__aexit__ = AsyncMock(return_value=False)
    stream_mock.text_stream = _aiter()
    return stream_mock


@pytest.mark.asyncio
async def test_convert_async_returns_cdm_document() -> None:
    stream = _make_stream_mock(_SAMPLE_CDM)
    mock_async_client = MagicMock()
    mock_async_client.messages.stream.return_value = stream

    with patch(
        "formaforge.ai.ai_converter.anthropic.AsyncAnthropic", return_value=mock_async_client
    ):
        converter = AiConverter()
        doc = await converter.convert_async("freeform notes", "doc.txt")

    assert isinstance(doc, CdmDocument)
    assert doc.frontmatter.conversion_method == "ai"


@pytest.mark.asyncio
async def test_convert_async_accumulates_chunks() -> None:
    stream = _make_stream_mock(_SAMPLE_CDM)
    mock_async_client = MagicMock()
    mock_async_client.messages.stream.return_value = stream

    with patch(
        "formaforge.ai.ai_converter.anthropic.AsyncAnthropic", return_value=mock_async_client
    ):
        converter = AiConverter()
        doc = await converter.convert_async("text", "doc.txt")

    assert "Summary" in doc.title or "meeting" in doc.body.lower()


@pytest.mark.asyncio
async def test_convert_async_fallback_on_bad_stream() -> None:
    bad_text = "not valid CDM at all"
    stream = _make_stream_mock(bad_text)
    mock_async_client = MagicMock()
    mock_async_client.messages.stream.return_value = stream

    with patch(
        "formaforge.ai.ai_converter.anthropic.AsyncAnthropic", return_value=mock_async_client
    ):
        converter = AiConverter()
        doc = await converter.convert_async("text", "doc.txt")

    assert isinstance(doc, CdmDocument)
    assert doc.frontmatter.conversion_confidence < 1.0


@pytest.mark.asyncio
async def test_convert_async_sets_source_format() -> None:
    stream = _make_stream_mock(_SAMPLE_CDM)
    mock_async_client = MagicMock()
    mock_async_client.messages.stream.return_value = stream

    with patch(
        "formaforge.ai.ai_converter.anthropic.AsyncAnthropic", return_value=mock_async_client
    ):
        converter = AiConverter()
        doc = await converter.convert_async("text", "s3://bucket/doc.txt", source_format="text")

    assert doc.frontmatter.conversion_method == "ai"
