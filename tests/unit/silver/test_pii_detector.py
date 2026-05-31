"""Tests for PiiDetector."""

import os
from unittest.mock import MagicMock, patch


def test_detect_returns_list() -> None:
    from formaforge.silver.pii_detector import PiiDetector

    result = PiiDetector().detect("Hello world")
    assert isinstance(result, list)


def test_detect_fallback_when_presidio_missing() -> None:
    from formaforge.silver.pii_detector import PiiDetector

    with patch("formaforge.silver.pii_detector._presidio_available", False):
        result = PiiDetector().detect("John Smith, john@example.com")
    assert result == []


def test_detect_returns_entity_types_when_presidio_available() -> None:
    from formaforge.silver.pii_detector import PiiDetector

    mock_result = MagicMock()
    mock_result.entity_type = "PERSON"
    mock_engine = MagicMock()
    mock_engine.analyze.return_value = [mock_result]

    with (
        patch("formaforge.silver.pii_detector._presidio_available", True),
        patch("formaforge.silver.pii_detector._get_analyzer", return_value=mock_engine),
    ):
        result = PiiDetector().detect("John Smith called")

    assert "PERSON" in result


def test_mask_identity_when_presidio_missing() -> None:
    from formaforge.silver.pii_detector import PiiDetector

    text = "John Smith, john@example.com"
    with patch("formaforge.silver.pii_detector._presidio_available", False):
        result = PiiDetector().mask(text)
    assert result == text


def test_mask_replaces_pii_when_presidio_available() -> None:
    from formaforge.silver.pii_detector import PiiDetector

    mock_anonymized = MagicMock()
    mock_anonymized.text = "<ANONYMIZED>"
    mock_anonymizer = MagicMock()
    mock_anonymizer.anonymize.return_value = mock_anonymized
    mock_analyzer = MagicMock()
    mock_analyzer.analyze.return_value = [MagicMock()]

    with (
        patch("formaforge.silver.pii_detector._presidio_available", True),
        patch("formaforge.silver.pii_detector._get_analyzer", return_value=mock_analyzer),
        patch("formaforge.silver.pii_detector._get_anonymizer", return_value=mock_anonymizer),
    ):
        result = PiiDetector().mask("John Smith called")

    assert result == "<ANONYMIZED>"


def test_skip_pii_env_var_bypasses_detection() -> None:
    from formaforge.silver.pii_detector import PiiDetector

    with patch.dict(os.environ, {"FORMAFORGE_SKIP_PII": "1"}):
        result = PiiDetector().detect("John Smith, SSN: 123-45-6789")
    assert result == []


def test_detect_deduplicates_entity_types() -> None:
    from formaforge.silver.pii_detector import PiiDetector

    mock_r1 = MagicMock()
    mock_r1.entity_type = "PERSON"
    mock_r2 = MagicMock()
    mock_r2.entity_type = "PERSON"
    mock_engine = MagicMock()
    mock_engine.analyze.return_value = [mock_r1, mock_r2]

    with (
        patch("formaforge.silver.pii_detector._presidio_available", True),
        patch("formaforge.silver.pii_detector._get_analyzer", return_value=mock_engine),
    ):
        result = PiiDetector().detect("John Smith and Jane Doe")

    assert result.count("PERSON") == 1
