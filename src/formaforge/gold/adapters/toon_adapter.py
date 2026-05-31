"""TOON (Token-Optimized Object Notation) Gold adapter."""

from typing import Any

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmTableBlock


def _toon_value(v: Any) -> str:
    if isinstance(v, dict):
        return _toon_dict(v)
    if isinstance(v, list):
        return _toon_list(v)
    if isinstance(v, str) and (" " in v or ":" in v or "{" in v):
        return f'"{v}"'
    return str(v)


def _toon_dict(d: dict[str, Any]) -> str:
    pairs = " ".join(f"{k}:{_toon_value(v)}" for k, v in d.items())
    return "{" + pairs + "}"


def _toon_list(lst: list[Any]) -> str:
    items = " ".join(_toon_value(item) for item in lst)
    return "[" + items + "]"


class ToonAdapter(BaseAdapter):
    adapter_name = "toon"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        parts: list[str] = []

        if doc.title:
            parts.append(f"#{doc.title}")

        if doc.body.strip():
            parts.append(doc.body.strip())

        for block in doc.blocks:
            if isinstance(block, CdmTableBlock):
                col_names = [c.split(":")[0] for c in block.columns]
                rows_toon = [
                    _toon_dict(dict(zip(col_names, row, strict=False))) for row in block.rows
                ]
                parts.append("[" + " ".join(rows_toon) + "]")
            elif isinstance(block, CdmDataBlock):
                content = block.content
                if isinstance(content, dict):
                    parts.append(_toon_dict(content))
                else:
                    parts.append(_toon_list(content))

        return "\n".join(parts)
