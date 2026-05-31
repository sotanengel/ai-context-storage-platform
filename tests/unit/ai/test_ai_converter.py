"""Tests for AI-assisted Silver converter (Anthropic SDK mocked)."""

from unittest.mock import MagicMock, patch

import pytest

from formaforge.ai.ai_converter import AiConverter
from formaforge.models.silver import CdmDocument

_SAMPLE_CDM = """\
---
source_format: pdf
source_uri: s3://test/doc.pdf
structure_class: unstructured
conversion_method: ai
conversion_confidence: 0.82
cdm_schema_version: "2.0"
pii_flags: []
---

# Meeting Notes

Discussion about project timeline.
"""


def _mock_anthropic(cdm_text: str) -> MagicMock:
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=cdm_text)]
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_ai_converter_returns_cdm_document() -> None:
    with patch(
        "formaforge.ai.ai_converter.anthropic.Anthropic", return_value=_mock_anthropic(_SAMPLE_CDM)
    ):
        converter = AiConverter()
        doc = converter.convert("Some freeform text about a meeting.", "doc.pdf")
    assert isinstance(doc, CdmDocument)
    assert doc.frontmatter.source_format == "pdf"


def test_ai_converter_sets_method_to_ai() -> None:
    with patch(
        "formaforge.ai.ai_converter.anthropic.Anthropic", return_value=_mock_anthropic(_SAMPLE_CDM)
    ):
        converter = AiConverter()
        doc = converter.convert("text", "notes.txt")
    assert doc.frontmatter.conversion_method == "ai"


def test_ai_converter_fallback_on_bad_response() -> None:
    bad_response = "This is not CDM at all, just garbage."
    with patch(
        "formaforge.ai.ai_converter.anthropic.Anthropic", return_value=_mock_anthropic(bad_response)
    ):
        converter = AiConverter()
        doc = converter.convert("text", "doc.pdf")
    assert isinstance(doc, CdmDocument)
    assert doc.frontmatter.conversion_confidence < 1.0


def test_ai_converter_no_api_key_raises() -> None:
    import os

    original = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        with pytest.raises((ValueError, Exception)):
            AiConverter(require_api_key=True)
    finally:
        if original:
            os.environ["ANTHROPIC_API_KEY"] = original
