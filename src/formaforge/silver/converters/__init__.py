"""Deterministic converters from source formats to CDM."""

from __future__ import annotations

from formaforge.silver.converters.base import BaseConverter
from formaforge.silver.converters.csv_converter import CsvConverter
from formaforge.silver.converters.docx_converter import DocxConverter
from formaforge.silver.converters.json_converter import JsonConverter
from formaforge.silver.converters.markdown_converter import MarkdownConverter
from formaforge.silver.converters.pdf_converter import PdfConverter
from formaforge.silver.converters.toml_converter import TomlConverter
from formaforge.silver.converters.xlsx_converter import XlsxConverter
from formaforge.silver.converters.xml_converter import XmlConverter
from formaforge.silver.converters.yaml_converter import YamlConverter

_BUILTIN_CONVERTERS: dict[str, BaseConverter] = {
    "json": JsonConverter(),
    "jsonl": JsonConverter(),
    "yaml": YamlConverter(),
    "csv": CsvConverter(),
    "tsv": CsvConverter(),
    "xml": XmlConverter(),
    "toml": TomlConverter(),
    "markdown": MarkdownConverter(),
    "pdf": PdfConverter(),
    "docx": DocxConverter(),
    "xlsx": XlsxConverter(),
}

_default_registry: ConverterRegistry | None = None


class ConverterRegistry:
    """Registry for deterministic Silver format converters."""

    def __init__(self) -> None:
        self._converters: dict[str, BaseConverter] = dict(_BUILTIN_CONVERTERS)

    @classmethod
    def default(cls) -> ConverterRegistry:
        global _default_registry
        if _default_registry is None:
            _default_registry = cls()
        return _default_registry

    def register(self, fmt: str, converter: BaseConverter) -> None:
        self._converters[fmt] = converter

    def get(self, fmt: str) -> BaseConverter | None:
        return self._converters.get(fmt)

    def all(self) -> dict[str, BaseConverter]:
        return dict(self._converters)


__all__ = [
    "BaseConverter",
    "ConverterRegistry",
    "CsvConverter",
    "DocxConverter",
    "JsonConverter",
    "MarkdownConverter",
    "PdfConverter",
    "TomlConverter",
    "XlsxConverter",
    "XmlConverter",
    "YamlConverter",
]
