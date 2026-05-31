"""Tests for CdmMigrator: version detection and v1.0→v2.0 migration."""

import pytest

from formaforge.models.silver import CdmDocument, CdmFrontmatter, ConversionMethod
from formaforge.silver.cdm_migrator import CdmMigrator

_V2_TEXT = """\
---
source_format: text
source_uri: doc.txt
structure_class: unstructured
conversion_method: ai
conversion_confidence: 0.85
cdm_schema_version: "2.0"
pii_flags: []
---

# Meeting Notes

Some content here.
"""

_V1_FRONTMATTER_TEXT = """\
---
source_format: text
source_uri: doc.txt
structure_class: unstructured
conversion_method: ai
conversion_confidence: 0.9
cdm_schema_version: "1.0"
pii_flags: []
---

# Old Document

Legacy content.
"""

_NO_FRONTMATTER_TEXT = """\
# Plain Markdown

This is plain markdown content without YAML frontmatter.
It represents a v1.0 legacy document.
"""


def _make_v2_doc() -> CdmDocument:
    fm = CdmFrontmatter(
        source_format="text",
        source_uri="doc.txt",
        structure_class="unstructured",
        conversion_method=ConversionMethod.AI,
        conversion_confidence=0.85,
        cdm_schema_version="2.0",
    )
    return CdmDocument(frontmatter=fm, title="Test", body="Some content.")


def _make_v1_doc() -> CdmDocument:
    fm = CdmFrontmatter(
        source_format="text",
        source_uri="doc.txt",
        structure_class="unstructured",
        conversion_method=ConversionMethod.AI,
        conversion_confidence=0.9,
        cdm_schema_version="1.0",
    )
    return CdmDocument(frontmatter=fm, title="Old Doc", body="Legacy content.")


class TestMigrateDoc:
    def test_migrate_v2_is_noop(self) -> None:
        doc = _make_v2_doc()
        migrator = CdmMigrator()
        result = migrator.migrate(doc)
        assert result is doc
        assert result.frontmatter.cdm_schema_version == "2.0"

    def test_migrate_v1_to_v2(self) -> None:
        doc = _make_v1_doc()
        result = CdmMigrator().migrate(doc)
        assert result.frontmatter.cdm_schema_version == "2.0"

    def test_migrate_v1_caps_confidence(self) -> None:
        doc = _make_v1_doc()
        doc.frontmatter.conversion_confidence = 0.95
        result = CdmMigrator().migrate(doc)
        assert result.frontmatter.conversion_confidence <= 0.5

    def test_migrate_v1_preserves_title_and_body(self) -> None:
        doc = _make_v1_doc()
        result = CdmMigrator().migrate(doc)
        assert result.title == "Old Doc"
        assert "Legacy" in result.body

    def test_migrate_unsupported_version_raises(self) -> None:
        doc = _make_v2_doc()
        doc.frontmatter.cdm_schema_version = "99.0"
        with pytest.raises(ValueError, match="Unsupported"):
            CdmMigrator().migrate(doc)

    def test_migrate_to_unsupported_target_raises(self) -> None:
        doc = _make_v2_doc()
        with pytest.raises(ValueError, match="Unsupported"):
            CdmMigrator().migrate(doc, target_version="3.0")


class TestMigrateText:
    def test_migrate_text_v2_returns_cdm_document(self) -> None:
        result = CdmMigrator().migrate_text(_V2_TEXT)
        assert isinstance(result, CdmDocument)
        assert result.frontmatter.cdm_schema_version == "2.0"

    def test_migrate_text_v1_frontmatter_upgrades(self) -> None:
        result = CdmMigrator().migrate_text(_V1_FRONTMATTER_TEXT)
        assert result.frontmatter.cdm_schema_version == "2.0"

    def test_migrate_text_no_frontmatter_creates_v2(self) -> None:
        result = CdmMigrator().migrate_text(_NO_FRONTMATTER_TEXT)
        assert isinstance(result, CdmDocument)
        assert result.frontmatter.cdm_schema_version == "2.0"

    def test_migrate_text_no_frontmatter_extracts_title(self) -> None:
        result = CdmMigrator().migrate_text(_NO_FRONTMATTER_TEXT)
        assert result.title == "Plain Markdown"

    def test_migrate_text_no_frontmatter_preserves_body(self) -> None:
        result = CdmMigrator().migrate_text(_NO_FRONTMATTER_TEXT)
        assert "plain markdown content" in result.body.lower()

    def test_migrate_text_no_frontmatter_low_confidence(self) -> None:
        result = CdmMigrator().migrate_text(_NO_FRONTMATTER_TEXT)
        assert result.frontmatter.conversion_confidence <= 0.5

    def test_migrate_text_accepts_source_uri(self) -> None:
        result = CdmMigrator().migrate_text(_NO_FRONTMATTER_TEXT, source_uri="s3://bucket/doc.md")
        assert result.frontmatter.source_uri == "s3://bucket/doc.md"
