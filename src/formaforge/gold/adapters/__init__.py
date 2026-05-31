"""Gold format adapters with AdapterRegistry singleton."""

from __future__ import annotations

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.gold.adapters.csv_adapter import CsvAdapter
from formaforge.gold.adapters.json_adapter import JsonAdapter
from formaforge.gold.adapters.jsonl_adapter import JsonlAdapter
from formaforge.gold.adapters.markdown_kv import MarkdownKvAdapter
from formaforge.gold.adapters.plaintext_adapter import PlaintextAdapter
from formaforge.gold.adapters.toon_adapter import ToonAdapter
from formaforge.gold.adapters.xml_adapter import XmlAdapter
from formaforge.gold.adapters.yaml_adapter import YamlAdapter

_BUILTIN_ADAPTERS: dict[str, BaseAdapter] = {
    "markdown_kv": MarkdownKvAdapter(),
    "yaml": YamlAdapter(),
    "csv": CsvAdapter(),
    "json": JsonAdapter(),
    "jsonl": JsonlAdapter(),
    "xml": XmlAdapter(),
    "plaintext": PlaintextAdapter(),
    "toon": ToonAdapter(),
}


class AdapterRegistry:
    """Singleton registry for Gold format adapters."""

    _instance: AdapterRegistry | None = None

    def __init__(self) -> None:
        self._adapters: dict[str, BaseAdapter] = dict(_BUILTIN_ADAPTERS)

    @classmethod
    def instance(cls) -> AdapterRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, adapter: BaseAdapter) -> None:
        self._adapters[name] = adapter

    def get(self, name: str) -> BaseAdapter | None:
        return self._adapters.get(name)

    def all(self) -> dict[str, BaseAdapter]:
        return dict(self._adapters)

    def list_names(self) -> list[str]:
        return list(self._adapters.keys())


__all__ = [
    "AdapterRegistry",
    "BaseAdapter",
    "CsvAdapter",
    "JsonAdapter",
    "JsonlAdapter",
    "MarkdownKvAdapter",
    "PlaintextAdapter",
    "ToonAdapter",
    "XmlAdapter",
    "YamlAdapter",
]
