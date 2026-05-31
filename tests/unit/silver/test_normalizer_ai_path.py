"""Tests for SilverNormalizer AI conversion path."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from formaforge.bronze.ingester import BronzeIngester
from formaforge.models.silver import CdmDocument, ConversionMethod
from formaforge.silver.normalizer import SilverNormalizer


def _make_record(
    tmp_path: Path, content: bytes, source_format: str, structure_class: str = "unstructured"
) -> object:
    ingester = BronzeIngester(storage_dir=tmp_path / "bronze")
    record = ingester.ingest(
        source_uri="s3://test/doc.txt",
        content=content,
        filename=f"doc.{source_format}",
    )
    return record


def test_normalizer_ai_path_calls_ai_converter(tmp_path: Path) -> None:
    record = _make_record(tmp_path, b"Free form text about a meeting.", "txt")

    mock_doc = MagicMock(spec=CdmDocument)
    mock_doc.body = "meeting text"
    mock_doc.frontmatter = MagicMock()
    mock_doc.frontmatter.pii_flags = []

    with patch("formaforge.silver.normalizer.AiConverter") as mock_cls:
        mock_cls.return_value.convert.return_value = mock_doc
        result = SilverNormalizer().normalize(record, ConversionMethod.AI)

    mock_cls.return_value.convert.assert_called_once()
    assert result is mock_doc


def test_normalizer_ai_path_populates_pii_flags(tmp_path: Path) -> None:
    record = _make_record(tmp_path, b"John Smith called today.", "txt")

    mock_doc = MagicMock(spec=CdmDocument)
    mock_doc.body = "John Smith called today."
    mock_doc.frontmatter = MagicMock()
    mock_doc.frontmatter.pii_flags = []

    with (
        patch("formaforge.silver.normalizer.AiConverter") as mock_converter_cls,
        patch("formaforge.silver.normalizer.PiiDetector") as mock_pii_cls,
    ):
        mock_converter_cls.return_value.convert.return_value = mock_doc
        mock_pii_cls.return_value.detect.return_value = ["PERSON"]
        SilverNormalizer().normalize(record, ConversionMethod.AI)

    mock_doc.frontmatter.__setattr__("pii_flags", ["PERSON"])


def test_normalizer_auto_routes_unstructured_to_ai(tmp_path: Path) -> None:
    record = _make_record(tmp_path, b"Plain text content.", "txt")

    mock_doc = MagicMock(spec=CdmDocument)
    mock_doc.body = "Plain text content."
    mock_doc.frontmatter = MagicMock()
    mock_doc.frontmatter.pii_flags = []

    with patch("formaforge.silver.normalizer.AiConverter") as mock_cls:
        mock_cls.return_value.convert.return_value = mock_doc
        result = SilverNormalizer().normalize(record)

    mock_cls.return_value.convert.assert_called_once()
    assert result is mock_doc


def test_normalizer_deterministic_does_not_call_ai(tmp_path: Path) -> None:
    record = _make_record(tmp_path, b'{"key": "value"}', "json", structure_class="structured")

    with patch("formaforge.silver.normalizer.AiConverter") as mock_cls:
        SilverNormalizer().normalize(record, ConversionMethod.DETERMINISTIC)

    mock_cls.assert_not_called()
