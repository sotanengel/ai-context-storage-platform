"""Tests for Bronze storage export (pack) pipeline."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from formaforge.bronze.checksums import sha256_of_bytes
from formaforge.bronze.ingester import BronzeIngester
from formaforge.export.guide import GuideGenerator
from formaforge.export.manifest import ARCHIVE_FORMAT_VERSION
from formaforge.export.packer import BronzePacker, EmptyBronzeStorageError
from formaforge.export.scanner import BronzeStorageScanner


@pytest.fixture()
def storage_with_records(tmp_path: Path) -> tuple[Path, BronzeIngester, list[str]]:
    storage_dir = tmp_path / "bronze"
    ingester = BronzeIngester(storage_dir=storage_dir)
    r1 = ingester.ingest("s3://a/data.json", b'{"x": 1}', "data.json")
    r2 = ingester.ingest("s3://b/notes.txt", b"hello", "notes.txt")
    return storage_dir, ingester, [r1.id, r2.id]


def test_scanner_builds_manifest(
    storage_with_records: tuple[Path, BronzeIngester, list[str]],
) -> None:
    storage_dir, _, ids = storage_with_records
    manifest = BronzeStorageScanner().scan(storage_dir)

    assert manifest.archive_format_version == ARCHIVE_FORMAT_VERSION
    assert len(manifest.records) == 2
    assert {r.bronze_id for r in manifest.records} == set(ids)
    for entry in manifest.records:
        assert entry.archive_path == f"bronze/{entry.bronze_id}/raw"
        assert entry.meta_path == f"bronze/{entry.bronze_id}/meta.json"
        raw_bytes = (storage_dir / entry.bronze_id / "raw").read_bytes()
        assert entry.raw_sha256 == sha256_of_bytes(raw_bytes)
        assert entry.raw_byte_count == len(raw_bytes)


def test_guide_contains_record_ids(
    storage_with_records: tuple[Path, BronzeIngester, list[str]],
) -> None:
    storage_dir, _, ids = storage_with_records
    manifest = BronzeStorageScanner().scan(storage_dir)
    guide = GuideGenerator().render(manifest)

    for bronze_id in ids:
        assert bronze_id in guide
        assert f'normalize_to_silver(bronze_id="{bronze_id}"' in guide
    assert "FORMAFORGE_AI_RESTORE_GUIDE" in guide or "manifest.json" in guide
    assert str(len(ids)) in guide or f"{len(ids)} record" in guide.lower()


def test_packer_creates_zip_layout(
    storage_with_records: tuple[Path, BronzeIngester, list[str]],
) -> None:
    storage_dir, _, ids = storage_with_records
    manifest = BronzeStorageScanner().scan(storage_dir)
    out = storage_dir.parent / "out.zip"
    BronzePacker().pack(manifest, storage_dir, out)

    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
        assert "manifest.json" in names
        assert "FORMAFORGE_AI_RESTORE_GUIDE.md" in names
        for bronze_id in ids:
            assert f"bronze/{bronze_id}/raw" in names
            assert f"bronze/{bronze_id}/meta.json" in names


def test_packer_empty_storage_raises(tmp_path: Path) -> None:
    empty = tmp_path / "empty-bronze"
    empty.mkdir()
    manifest = BronzeStorageScanner().scan(empty)
    with pytest.raises(EmptyBronzeStorageError):
        BronzePacker().pack(manifest, empty, tmp_path / "out.zip")


def test_roundtrip_checksum(storage_with_records: tuple[Path, BronzeIngester, list[str]]) -> None:
    storage_dir, _, _ = storage_with_records
    manifest = BronzeStorageScanner().scan(storage_dir)
    out = storage_dir.parent / "roundtrip.zip"
    BronzePacker().pack(manifest, storage_dir, out)

    extract_dir = storage_dir.parent / "extracted"
    extract_dir.mkdir()
    with zipfile.ZipFile(out) as zf:
        zf.extractall(extract_dir)

    loaded = json.loads((extract_dir / "manifest.json").read_text())
    for entry in loaded["records"]:
        raw_path = extract_dir / entry["archive_path"]
        assert sha256_of_bytes(raw_path.read_bytes()) == entry["raw_sha256"]
