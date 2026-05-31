"""Integration: Bronze ingest → Silver normalize roundtrip."""

import json
from pathlib import Path

import pytest

from formaforge.bronze.ingester import BronzeIngester
from formaforge.models.silver import CdmTableBlock
from formaforge.silver.cdm_parser import CdmParser
from formaforge.silver.cdm_writer import CdmWriter
from formaforge.silver.normalizer import SilverNormalizer


@pytest.fixture()
def ingester(tmp_path: Path) -> BronzeIngester:
    return BronzeIngester(storage_dir=tmp_path / "bronze")


@pytest.fixture()
def normalizer() -> SilverNormalizer:
    return SilverNormalizer()


def test_json_array_roundtrip(ingester: BronzeIngester, normalizer: SilverNormalizer) -> None:
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    record = ingester.ingest("s3://test/data.json", json.dumps(data).encode(), "data.json")
    doc = normalizer.normalize(record)
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    tb = next(b for b in recovered.blocks if isinstance(b, CdmTableBlock))
    assert tb.rows[0][1] == "Alice"


def test_csv_roundtrip(ingester: BronzeIngester, normalizer: SilverNormalizer) -> None:
    csv_data = b"col1,col2\nfoo,bar\nbaz,qux\n"
    record = ingester.ingest("s3://test/data.csv", csv_data, "data.csv")
    doc = normalizer.normalize(record)
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    tb = next(b for b in recovered.blocks if isinstance(b, CdmTableBlock))
    assert tb.rows[0][0] == "foo"


def test_markdown_roundtrip(ingester: BronzeIngester, normalizer: SilverNormalizer) -> None:
    md = b"# My Doc\n\nSome content here.\n"
    record = ingester.ingest("file://doc.md", md, "doc.md")
    doc = normalizer.normalize(record)
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    assert "My Doc" in recovered.title or "My Doc" in recovered.body


def test_both_docs_produce_canonical_markdown_format(
    ingester: BronzeIngester,
    normalizer: SilverNormalizer,
) -> None:
    json_record = ingester.ingest("s3://a.json", json.dumps([{"x": 1}]).encode(), "a.json")
    md_record = ingester.ingest("file://b.md", b"# Title\n\nbody\n", "b.md")

    json_doc = normalizer.normalize(json_record)
    md_doc = normalizer.normalize(md_record)

    json_text = CdmWriter().write(json_doc)
    md_text = CdmWriter().write(md_doc)

    assert json_text.startswith("---\n")
    assert md_text.startswith("---\n")
    assert "cdm_schema_version:" in json_text
    assert "cdm_schema_version:" in md_text
