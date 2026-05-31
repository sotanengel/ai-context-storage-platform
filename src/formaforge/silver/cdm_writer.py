"""Serialize CdmDocument to CDM Markdown text."""

from typing import Any

import yaml

from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmTableBlock


class CdmWriter:
    def write(self, doc: CdmDocument) -> str:
        parts: list[str] = []

        fm = doc.frontmatter.model_dump(mode="json")
        parts.append("---")
        parts.append(yaml.dump(fm, allow_unicode=True, sort_keys=True).rstrip())
        parts.append("---")
        parts.append("")

        if doc.title:
            parts.append(f"# {doc.title}")
            parts.append("")

        if doc.body:
            parts.append(doc.body.strip())
            parts.append("")

        for block in doc.blocks:
            if isinstance(block, CdmTableBlock):
                parts.append(self._write_table(block))
            elif isinstance(block, CdmDataBlock):
                parts.append(self.write_data_block(block))
            parts.append("")

        return "\n".join(parts)

    def _write_table(self, block: CdmTableBlock) -> str:
        rows_yaml = yaml.dump(
            [list(row) for row in block.rows],
            allow_unicode=True,
            default_flow_style=None,
        ).rstrip()
        columns_str = ", ".join(block.columns)
        lines = [
            "```table",
            f"columns: [{columns_str}]",
            f"rows:\n{self._indent(rows_yaml, 2)}",
            "```",
        ]
        return "\n".join(lines)

    def write_data_block(self, block: CdmDataBlock) -> str:
        content_yaml = yaml.dump(block.content, allow_unicode=True, sort_keys=True).rstrip()
        return f"```data\n{content_yaml}\n```"

    def _write_data(self, block: CdmDataBlock) -> str:
        return self.write_data_block(block)

    def _indent(self, text: str, spaces: int) -> str:
        prefix = " " * spaces
        return "\n".join(prefix + line for line in text.splitlines())

    def _serialize_value(self, v: Any) -> str:
        if isinstance(v, str):
            return f'"{v}"'
        return str(v)
