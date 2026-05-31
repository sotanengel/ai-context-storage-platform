"""Parse CDM Markdown text back to CdmDocument."""

import re
from typing import Any

import yaml

from formaforge.models.silver import (
    CdmBlock,
    CdmDataBlock,
    CdmDocument,
    CdmFrontmatter,
    CdmTableBlock,
)

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_FENCE_BLOCK_RE = re.compile(r"```(table|data)\n(.*?)```", re.DOTALL)
_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


class CdmParser:
    def parse(self, text: str) -> CdmDocument:
        frontmatter, rest = self._extract_frontmatter(text)
        title = self._extract_title(rest)
        blocks = self._extract_blocks(rest)
        body = self._extract_body(rest)

        return CdmDocument(frontmatter=frontmatter, title=title, body=body, blocks=blocks)

    def _extract_frontmatter(self, text: str) -> tuple[CdmFrontmatter, str]:
        m = _FRONTMATTER_RE.match(text)
        if not m:
            raise ValueError("CDM document missing YAML frontmatter")
        raw = yaml.safe_load(m.group(1)) or {}
        fm = CdmFrontmatter(**{k: v for k, v in raw.items() if k in CdmFrontmatter.model_fields})
        return fm, text[m.end() :]

    def _extract_title(self, text: str) -> str:
        m = _H1_RE.search(text)
        return m.group(1).strip() if m else ""

    def _extract_blocks(self, text: str) -> list[CdmBlock]:
        blocks: list[CdmBlock] = []
        for m in _FENCE_BLOCK_RE.finditer(text):
            kind = m.group(1)
            content = m.group(2)
            if kind == "table":
                blocks.append(self._parse_table_block(content))
            elif kind == "data":
                blocks.append(self._parse_data_block(content))
        return blocks

    def _parse_table_block(self, content: str) -> CdmTableBlock:
        parsed = yaml.safe_load(content) or {}
        raw_columns = parsed.get("columns", [])
        if isinstance(raw_columns, str):
            columns = [c.strip() for c in raw_columns.split(",")]
        else:
            columns = [str(c) for c in raw_columns]
        raw_rows = parsed.get("rows", [])
        rows: list[list[Any]] = [list(row) for row in raw_rows] if raw_rows else []
        return CdmTableBlock(columns=columns, rows=rows)

    def _parse_data_block(self, content: str) -> CdmDataBlock:
        data = yaml.safe_load(content)
        return CdmDataBlock(content=data)

    def _extract_body(self, text: str) -> str:
        body = _FENCE_BLOCK_RE.sub("", text)
        body = _H1_RE.sub("", body)
        return body.strip()
