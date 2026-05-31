"""Markdown key-value adapter."""

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmTableBlock
from formaforge.silver.cdm_writer import CdmWriter


class MarkdownKvAdapter(BaseAdapter):
    adapter_name = "markdown_kv"

    def render(self, doc: CdmDocument, **opts: str) -> str:
        parts: list[str] = []
        if doc.title:
            parts.append(f"# {doc.title}\n")
        if doc.body:
            parts.append(doc.body.strip() + "\n")
        for block in doc.blocks:
            if isinstance(block, CdmTableBlock):
                parts.append(self._table_to_markdown(block))
            elif isinstance(block, CdmDataBlock):
                parts.append(self._data_to_markdown(block))
        return "\n".join(parts)

    def _table_to_markdown(self, block: CdmTableBlock) -> str:
        col_names = [c.split(":")[0] for c in block.columns]
        header = "| " + " | ".join(col_names) + " |"
        sep = "| " + " | ".join("---" for _ in col_names) + " |"
        rows = ["| " + " | ".join(str(v) for v in row) + " |" for row in block.rows]
        return "\n".join([header, sep] + rows)

    def _data_to_markdown(self, block: CdmDataBlock) -> str:
        writer = CdmWriter()
        return writer.write_data_block(block)
