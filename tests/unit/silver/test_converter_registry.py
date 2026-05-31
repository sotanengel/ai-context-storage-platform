"""Tests for ConverterRegistry."""

from formaforge.silver.converters import ConverterRegistry
from formaforge.silver.converters.base import BaseConverter
from formaforge.silver.converters.json_converter import JsonConverter


class _StubConverter(BaseConverter):
    source_format = "stub"

    def convert(self, raw: str, source_uri: str = "") -> object:
        raise NotImplementedError


def test_default_registry_has_json_converter() -> None:
    registry = ConverterRegistry.default()
    converter = registry.get("json")
    assert converter is not None
    assert isinstance(converter, JsonConverter)


def test_get_unknown_returns_none() -> None:
    registry = ConverterRegistry.default()
    assert registry.get("nonexistent_xyz") is None


def test_register_and_get() -> None:
    registry = ConverterRegistry()
    stub = _StubConverter()
    registry.register("custom_fmt", stub)
    assert registry.get("custom_fmt") is stub
