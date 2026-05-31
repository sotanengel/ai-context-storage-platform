"""Tests for GoldMaterializer dependency injection and error paths."""

from unittest.mock import MagicMock

import pytest

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.gold.materializer import GoldMaterializer
from formaforge.models.gold import GoldRequest
from formaforge.models.silver import CdmDocument, CdmFrontmatter


class _StubAdapter(BaseAdapter):
    adapter_name = "stub"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        return "hello world"


def _make_doc() -> CdmDocument:
    fm = CdmFrontmatter(source_format="json", source_uri="", structure_class="structured")
    return CdmDocument(frontmatter=fm, title="T", body="secret@example.com")


def test_materialize_unknown_adapter_raises() -> None:
    registry = MagicMock()
    registry.get.return_value = None
    materializer = GoldMaterializer(registry=registry)
    request = GoldRequest(silver_id="s1", adapter_name="nonexistent")

    with pytest.raises(ValueError, match="Unknown adapter"):
        materializer.materialize(_make_doc(), request)


def test_materialize_pii_mask_uses_injected_detector() -> None:
    registry = MagicMock()
    registry.get.return_value = _StubAdapter()
    pii_detector = MagicMock()
    pii_detector.mask.return_value = "masked output"

    materializer = GoldMaterializer(registry=registry, pii_detector=pii_detector)
    request = GoldRequest(silver_id="s1", adapter_name="stub", pii_mask=True)
    result = materializer.materialize(_make_doc(), request)

    pii_detector.mask.assert_called_once_with("hello world")
    assert result.text == "masked output"
