"""YAML Gold adapter."""

from typing import Any

import yaml

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmTableBlock


class YamlAdapter(BaseAdapter):
    adapter_name = "yaml"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        payload: dict[str, Any] = {}
        if doc.title:
            payload["title"] = doc.title
        for i, block in enumerate(doc.blocks):
            key = f"block_{i}" if len(doc.blocks) > 1 else "data"
            if isinstance(block, CdmTableBlock):
                col_names = [c.split(":")[0] for c in block.columns]
                payload[key] = [dict(zip(col_names, row, strict=True)) for row in block.rows]
            elif isinstance(block, CdmDataBlock):
                payload[key] = block.content
        if doc.body and not payload:
            payload["content"] = doc.body
        return yaml.dump(payload, allow_unicode=True, sort_keys=False)
