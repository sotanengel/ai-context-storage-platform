"""Plain text Gold adapter: strips all markup."""

import re

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmTableBlock

_FENCE_RE = re.compile(r"```\w*\n.*?```", re.DOTALL)
_HEADING_RE = re.compile(r"^#+\s+", re.MULTILINE)


class PlaintextAdapter(BaseAdapter):
    adapter_name = "plaintext"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        parts: list[str] = []
        if doc.title:
            parts.append(doc.title)
        if doc.body:
            clean = _FENCE_RE.sub("", doc.body)
            clean = _HEADING_RE.sub("", clean)
            parts.append(clean.strip())
        for block in doc.blocks:
            if isinstance(block, CdmTableBlock):
                col_names = [c.split(":")[0] for c in block.columns]
                parts.append(", ".join(col_names))
                for row in block.rows:
                    parts.append(", ".join(str(v) for v in row))
            elif isinstance(block, CdmDataBlock):
                parts.append(str(block.content))
        return "\n\n".join(p for p in parts if p)
