"""Tests for CDM writer and parser roundtrip."""

from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmFrontmatter, CdmTableBlock
from formaforge.silver.cdm_parser import CdmParser
from formaforge.silver.cdm_writer import CdmWriter


def _make_doc(**kwargs: object) -> CdmDocument:
    fm = CdmFrontmatter(source_format="json", source_uri="s3://test", structure_class="structured")
    return CdmDocument(frontmatter=fm, **kwargs)  # type: ignore[arg-type]


def test_write_produces_yaml_frontmatter() -> None:
    doc = _make_doc(title="Test")
    text = CdmWriter().write(doc)
    assert text.startswith("---\n")
    assert "source_format: json" in text
    assert "---" in text


def test_write_includes_title() -> None:
    doc = _make_doc(title="My Title")
    text = CdmWriter().write(doc)
    assert "# My Title" in text


def test_write_table_block() -> None:
    block = CdmTableBlock(
        columns=["id:int", "name:string"],
        rows=[[1, "Alice"], [2, "Bob"]],
    )
    doc = _make_doc(title="T", blocks=[block])
    text = CdmWriter().write(doc)
    assert "```table" in text
    assert "id:int" in text
    assert "Alice" in text


def test_write_data_block() -> None:
    block = CdmDataBlock(content={"nested": {"key": "value"}})
    doc = _make_doc(title="D", blocks=[block])
    text = CdmWriter().write(doc)
    assert "```data" in text
    assert "nested:" in text


def test_parse_minimal_cdm() -> None:
    text = """---
source_format: json
source_uri: s3://test
structure_class: structured
conversion_method: deterministic
conversion_confidence: 1.0
cdm_schema_version: "2.0"
pii_flags: []
---

# Title

body text
"""
    doc = CdmParser().parse(text)
    assert doc.frontmatter.source_format == "json"
    assert doc.title == "Title"
    assert "body text" in doc.body


def test_roundtrip_table_block() -> None:
    block = CdmTableBlock(
        columns=["order_id:int", "amount:decimal"],
        rows=[[1001, 12000.0], [1002, 8400.5]],
    )
    original = _make_doc(title="Orders", blocks=[block])
    text = CdmWriter().write(original)
    recovered = CdmParser().parse(text)
    assert recovered.title == "Orders"
    assert len(recovered.blocks) == 1
    tb = recovered.blocks[0]
    assert isinstance(tb, CdmTableBlock)
    assert tb.columns == block.columns
    assert tb.rows[0][0] == block.rows[0][0]


def test_roundtrip_data_block() -> None:
    block = CdmDataBlock(content={"customer": {"id": 123, "name": "Alice"}})
    original = _make_doc(title="Customer", blocks=[block])
    text = CdmWriter().write(original)
    recovered = CdmParser().parse(text)
    db = recovered.blocks[0]
    assert isinstance(db, CdmDataBlock)
    assert db.content["customer"]["id"] == 123  # type: ignore[index]


def test_parse_spec_sample() -> None:
    """Verify the CDM sample from the spec parses correctly."""
    text = """\
---
source_format: json
source_uri: s3://bronze/orders/2026q1.json
structure_class: structured
normalized_at: 2026-05-30T09:00:00Z
conversion_method: deterministic
conversion_confidence: 1.0
cdm_schema_version: "2.0"
pii_flags: [customer_name]
---

# 注文レコード（2026 Q1）

source: orders API / 均一配列＋顧客ネスト

```table
columns: [order_id:int, region:string, amount:decimal, ordered_at:date]
rows:
  - [1001, "APAC", 12000.00, 2026-01-05]
  - [1002, "EMEA",  8400.50, 2026-01-06]
```

```data
customer:
  id: 123
  profile:
    name: "*"
```
"""
    doc = CdmParser().parse(text)
    assert doc.frontmatter.source_format == "json"
    assert doc.frontmatter.pii_flags == ["customer_name"]
    assert "注文レコード" in doc.title
    table_blocks = [b for b in doc.blocks if isinstance(b, CdmTableBlock)]
    data_blocks = [b for b in doc.blocks if isinstance(b, CdmDataBlock)]
    assert len(table_blocks) == 1
    assert len(data_blocks) == 1
    assert table_blocks[0].rows[0][0] == 1001
