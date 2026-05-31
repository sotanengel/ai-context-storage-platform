"""Tests for AdapterRegistry singleton."""

from formaforge.gold.adapters import AdapterRegistry
from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDocument, CdmFrontmatter


class _DummyAdapter(BaseAdapter):
    adapter_name = "dummy"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        return "dummy"


def test_registry_is_singleton() -> None:
    r1 = AdapterRegistry.instance()
    r2 = AdapterRegistry.instance()
    assert r1 is r2


def test_registry_has_builtin_adapters() -> None:
    registry = AdapterRegistry.instance()
    names = registry.list_names()
    assert "yaml" in names
    assert "json" in names
    assert "csv" in names
    assert "jsonl" in names
    assert "xml" in names
    assert "markdown_kv" in names
    assert "plaintext" in names


def test_registry_get_known_adapter() -> None:
    registry = AdapterRegistry.instance()
    adapter = registry.get("yaml")
    assert adapter is not None
    assert isinstance(adapter, BaseAdapter)


def test_registry_get_unknown_returns_none() -> None:
    registry = AdapterRegistry.instance()
    assert registry.get("nonexistent_xyz") is None


def test_registry_register_and_get() -> None:
    registry = AdapterRegistry.instance()
    registry.register("dummy_test", _DummyAdapter())
    adapter = registry.get("dummy_test")
    assert adapter is not None
    fm = CdmFrontmatter(source_format="json", source_uri="", structure_class="structured")
    doc = CdmDocument(frontmatter=fm)
    assert adapter.render(doc) == "dummy"


def test_registry_all_returns_dict() -> None:
    registry = AdapterRegistry.instance()
    all_adapters = registry.all()
    assert isinstance(all_adapters, dict)
    assert "yaml" in all_adapters


def test_registry_reset_clears_custom_adapters() -> None:
    registry = AdapterRegistry.instance()
    registry.register("dummy_test", _DummyAdapter())
    assert registry.get("dummy_test") is not None

    AdapterRegistry.reset_for_testing()
    fresh = AdapterRegistry.instance()
    assert fresh.get("dummy_test") is None
    assert fresh.get("yaml") is not None
