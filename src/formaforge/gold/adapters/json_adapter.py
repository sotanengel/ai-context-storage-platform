"""JSON Gold adapter."""

import json
from typing import Any

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmTableBlock


class JsonAdapter(BaseAdapter):
    adapter_name = "json"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        pretty = opts.get("pretty", "true").lower() != "false"
        payload = self._to_dict(doc)
        indent = 2 if pretty else None
        separators = None if pretty else (",", ":")
        return json.dumps(payload, ensure_ascii=False, indent=indent, separators=separators)

    def _to_dict(self, doc: CdmDocument) -> Any:
        result: dict[str, Any] = {}
        if doc.title:
            result["title"] = doc.title
        blocks_data: list[object] = []
        for block in doc.blocks:
            if isinstance(block, CdmTableBlock):
                col_names = [c.split(":")[0] for c in block.columns]
                blocks_data.extend(dict(zip(col_names, row, strict=True)) for row in block.rows)
            elif isinstance(block, CdmDataBlock):
                blocks_data.append(block.content)
        if len(blocks_data) == 1:
            return blocks_data[0]
        if blocks_data:
            result["data"] = blocks_data
        if doc.body:
            result["content"] = doc.body
        return result
