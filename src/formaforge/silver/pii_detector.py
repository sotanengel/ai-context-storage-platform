"""Backward-compatible re-export of PiiDetector from the privacy module."""

from formaforge.privacy import pii_detector as _privacy_pii
from formaforge.privacy.pii_detector import PiiDetector

_get_analyzer = _privacy_pii._get_analyzer
_get_anonymizer = _privacy_pii._get_anonymizer
_presidio_available = _privacy_pii._presidio_available

__all__ = ["PiiDetector", "_get_analyzer", "_get_anonymizer", "_presidio_available"]
