"""Silver converter: PDF → CDM via PyMuPDF (fitz)."""

from __future__ import annotations

import io
from typing import Any

from formaforge.models.silver import CdmDocument, CdmFrontmatter, ConversionMethod
from formaforge.silver.converters.base import BaseConverter


def _open_pdf(data: bytes) -> list[Any]:
    """Open PDF bytes and return list of page objects (fitz.Page)."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise ImportError(
            "PyMuPDF is required for PDF ingestion. Install with: uv add 'formaforge[binary]'"
        ) from exc
    doc = fitz.open(stream=io.BytesIO(data), filetype="pdf")
    return list(doc)


class PdfConverter(BaseConverter):
    """Convert PDF bytes to a CDM document."""

    source_format = "pdf"

    def convert(self, raw: str, source_uri: str = "") -> CdmDocument:
        return self.convert_bytes(raw.encode("utf-8", errors="replace"), source_uri)

    def convert_bytes(self, raw: bytes, source_uri: str = "") -> CdmDocument:
        pages = _open_pdf(raw)
        texts: list[str] = []
        for page in pages:
            text = page.get_text()
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())

        body = "\n\n".join(texts)
        fm = CdmFrontmatter(
            source_format=self.source_format,
            source_uri=source_uri,
            structure_class="unstructured",
            conversion_method=ConversionMethod.DETERMINISTIC,
            conversion_confidence=0.9,
        )
        return CdmDocument(frontmatter=fm, body=body)
