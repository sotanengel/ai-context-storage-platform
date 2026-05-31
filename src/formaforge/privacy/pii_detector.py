"""PII detection and masking via presidio-analyzer (optional dependency)."""

from __future__ import annotations

import os
from typing import Any

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine

    _presidio_available = True
except ImportError:
    _presidio_available = False


def _get_analyzer() -> Any:
    return AnalyzerEngine()


def _get_anonymizer() -> Any:
    return AnonymizerEngine()


class PiiDetector:
    """Detect and mask PII entities in text using presidio-analyzer."""

    def detect(self, text: str) -> list[str]:
        """Return deduplicated list of detected PII entity types."""
        if os.environ.get("FORMAFORGE_SKIP_PII") == "1":
            return []
        if not _presidio_available:
            return []
        analyzer = _get_analyzer()
        results = analyzer.analyze(text=text, language="en")
        return list(dict.fromkeys(r.entity_type for r in results))

    def mask(self, text: str) -> str:
        """Replace PII entities with anonymized placeholders."""
        if not _presidio_available:
            return text
        analyzer = _get_analyzer()
        analyzer_results = analyzer.analyze(text=text, language="en")
        if not analyzer_results:
            return text
        anonymizer = _get_anonymizer()
        result = anonymizer.anonymize(text=text, analyzer_results=analyzer_results)
        return str(result.text)
