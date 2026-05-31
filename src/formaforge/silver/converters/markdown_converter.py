"""Markdown → CDM normalizing converter."""

import re

import yaml

from formaforge.models.silver import CdmDocument, CdmFrontmatter, ConversionMethod
from formaforge.silver.converters.base import BaseConverter

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


class MarkdownConverter(BaseConverter):
    source_format = "markdown"

    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        existing_fm: dict[str, object] = {}
        body = raw

        m = _FRONTMATTER_RE.match(raw)
        if m:
            existing_fm = yaml.safe_load(m.group(1)) or {}
            body = raw[m.end() :]

        h1 = _H1_RE.search(body)
        title = h1.group(1).strip() if h1 else ""
        if h1:
            body = _H1_RE.sub("", body, count=1).strip()

        fm = CdmFrontmatter(
            source_format=self.source_format,
            source_uri=source_uri,
            structure_class="structured",
            conversion_method=ConversionMethod.DETERMINISTIC,
            conversion_confidence=1.0,
        )
        for key, value in existing_fm.items():
            if key in CdmFrontmatter.model_fields and key not in (
                "source_format",
                "conversion_method",
            ):
                object.__setattr__(fm, key, value)

        return CdmDocument(frontmatter=fm, title=title, body=body)
