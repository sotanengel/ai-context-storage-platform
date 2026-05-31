"""Tests for Bronze ingestion service."""

import json
from pathlib import Path

import pytest

from formaforge.bronze.ingester import BronzeIngester
from formaforge.models.bronze import StructureClass


@pytest.fixture()
def ingester(tmp_path: Path) -> BronzeIngester:
    storage_dir = tmp_path / ".formaforge" / "bronze"
    return BronzeIngester(storage_dir=storage_dir)


def test_ingest_json_returns_record(ingester: BronzeIngester, tmp_path: Path) -> None:
    content = json.dumps({"order_id": 1, "amount": 99.99}).encode()
    record = ingester.ingest(
        source_uri="s3://bucket/orders.json",
        content=content,
        filename="orders.json",
    )
    assert record.source_uri == "s3://bucket/orders.json"
    assert record.source_format == "json"
    assert record.structure_class == StructureClass.STRUCTURED
    assert len(record.checksum) == 64
    assert record.ingested_at is not None


def test_ingest_stores_raw_file(ingester: BronzeIngester, tmp_path: Path) -> None:
    content = b"name,age\nAlice,30\n"
    record = ingester.ingest(
        source_uri="file://data.csv",
        content=content,
        filename="data.csv",
    )
    stored = Path(record.raw_content_path).read_bytes()
    assert stored == content


def test_ingest_dedup_same_checksum(ingester: BronzeIngester) -> None:
    content = b'{"x": 1}'
    record1 = ingester.ingest("uri://a.json", content, "a.json")
    record2 = ingester.ingest("uri://b.json", content, "b.json")
    assert record1.id == record2.id


def test_ingest_different_content_creates_new_record(ingester: BronzeIngester) -> None:
    record1 = ingester.ingest("uri://a.json", b'{"x": 1}', "a.json")
    record2 = ingester.ingest("uri://b.json", b'{"x": 2}', "b.json")
    assert record1.id != record2.id


def test_ingest_csv_detects_structure_class(ingester: BronzeIngester) -> None:
    content = b"col1,col2\nval1,val2\n"
    record = ingester.ingest("uri://data.csv", content, "data.csv")
    assert record.structure_class == StructureClass.STRUCTURED


def test_ingest_text_detects_unstructured(ingester: BronzeIngester) -> None:
    content = b"Just some free-form text without structure."
    record = ingester.ingest("uri://notes.txt", content, "notes.txt")
    assert record.structure_class == StructureClass.UNSTRUCTURED


def test_ingester_uses_formaforge_storage_dir_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_dir = tmp_path / "env-bronze"
    monkeypatch.setenv("FORMAFORGE_STORAGE_DIR", str(storage_dir))
    ingester = BronzeIngester()
    content = b'{"x": 1}'
    record = ingester.ingest("uri://data.json", content, "data.json")
    assert Path(record.raw_content_path).parent.parent == storage_dir
