"""CDM schema version detection and migration (v1.0 → v2.0)."""

import re

from formaforge.models.silver import CdmDocument, CdmFrontmatter, ConversionMethod
from formaforge.silver.cdm_parser import CdmParser

_H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

_SUPPORTED_VERSIONS = {"1.0", "2.0"}
CURRENT_VERSION = "2.0"


class CdmMigrator:
    def migrate(self, doc: CdmDocument, target_version: str = CURRENT_VERSION) -> CdmDocument:
        """Upgrade CdmDocument to target_version. Idempotent if already at target."""
        current = doc.frontmatter.cdm_schema_version
        if current == target_version:
            return doc
        if current not in _SUPPORTED_VERSIONS:
            raise ValueError(f"Unsupported migration: source version {current!r} is unknown")
        if target_version not in _SUPPORTED_VERSIONS:
            raise ValueError(f"Unsupported migration: target version {target_version!r} is unknown")
        if current == "1.0" and target_version == "2.0":
            return self._v1_to_v2(doc)
        raise ValueError(f"Unsupported migration: {current!r} → {target_version!r}")

    def migrate_text(self, text: str, source_uri: str = "") -> CdmDocument:
        """Parse CDM text (any version) and return a v2.0 CdmDocument.

        Handles both v2.0 documents (YAML frontmatter present) and legacy v1.0
        documents (plain Markdown with no frontmatter).
        """
        if not text.strip().startswith("---"):
            doc = self._make_v1_doc(text, source_uri)
            return self.migrate(doc)
        doc = CdmParser().parse(text)
        return self.migrate(doc)

    def _v1_to_v2(self, doc: CdmDocument) -> CdmDocument:
        doc.frontmatter.cdm_schema_version = "2.0"
        if not doc.frontmatter.conversion_method:
            doc.frontmatter.conversion_method = ConversionMethod.AI
        doc.frontmatter.conversion_confidence = min(doc.frontmatter.conversion_confidence, 0.5)
        return doc

    def _make_v1_doc(self, text: str, source_uri: str) -> CdmDocument:
        m = _H1_RE.search(text)
        title = m.group(1).strip() if m else ""
        body = _H1_RE.sub("", text).strip()
        fm = CdmFrontmatter(
            source_format="markdown",
            source_uri=source_uri,
            structure_class="unstructured",
            conversion_method=ConversionMethod.AI,
            conversion_confidence=0.5,
            cdm_schema_version="1.0",
        )
        return CdmDocument(frontmatter=fm, title=title, body=body)
