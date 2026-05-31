"""Base class for all deterministic source-format converters."""

from abc import ABC, abstractmethod
from typing import Any

from formaforge.models.silver import (
    CdmBlock,
    CdmDataBlock,
    CdmDocument,
    CdmFrontmatter,
    CdmTableBlock,
    ConversionMethod,
)


class BaseConverter(ABC):
    source_format: str = ""

    @abstractmethod
    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        """Convert raw text to a CdmDocument."""

    def _make_frontmatter(self, source_uri: str) -> CdmFrontmatter:
        return CdmFrontmatter(
            source_format=self.source_format,
            source_uri=source_uri,
            structure_class="structured",
            conversion_method=ConversionMethod.DETERMINISTIC,
            conversion_confidence=1.0,
        )

    def _classify_payload(self, data: Any) -> list[CdmBlock]:
        if isinstance(data, list) and data:
            if self._is_uniform_object_array(data):
                return [self._build_table_block(data)]
            return [CdmDataBlock(content=data)]
        if isinstance(data, dict):
            return [CdmDataBlock(content=dict(sorted(data.items())))]
        return []

    def _is_uniform_object_array(self, data: list[Any]) -> bool:
        if not all(isinstance(item, dict) for item in data):
            return False
        keys = [frozenset(item.keys()) for item in data]
        return len(set(keys)) == 1

    def _build_table_block(self, data: list[dict[str, Any]]) -> CdmTableBlock:
        keys = sorted(data[0].keys())
        columns = [f"{k}:{self._infer_type(data[0][k])}" for k in keys]
        rows = [[item[k] for k in keys] for item in data]
        return CdmTableBlock(columns=columns, rows=rows)

    def _infer_type(self, value: Any) -> str:
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "decimal"
        return "string"
