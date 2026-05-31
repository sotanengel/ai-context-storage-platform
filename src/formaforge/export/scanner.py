"""Scan Bronze storage directories into an archive manifest."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from formaforge import __version__
from formaforge.bronze.checksums import sha256_of_bytes
from formaforge.export.manifest import ARCHIVE_FORMAT_VERSION, ArchiveManifest, ArchiveRecordEntry
from formaforge.models.bronze import BronzeRecord


class InvalidBronzeStorageError(ValueError):
    """Raised when a Bronze storage directory entry is malformed."""


class BronzeStorageScanner:
    def scan(self, storage_dir: Path) -> ArchiveManifest:
        storage_dir = storage_dir.resolve()
        if not storage_dir.is_dir():
            raise InvalidBronzeStorageError(f"not a directory: {storage_dir}")

        records: list[ArchiveRecordEntry] = []
        for child in sorted(storage_dir.iterdir()):
            if not child.is_dir():
                continue
            meta_path = child / "meta.json"
            raw_path = child / "raw"
            if not meta_path.is_file():
                continue
            if not raw_path.is_file():
                raise InvalidBronzeStorageError(
                    f"missing raw file for record {child.name}: {raw_path}"
                )

            record = BronzeRecord.model_validate_json(meta_path.read_text())
            raw_bytes = raw_path.read_bytes()
            raw_sha256 = sha256_of_bytes(raw_bytes)
            if raw_sha256 != record.checksum:
                raise InvalidBronzeStorageError(
                    f"checksum mismatch for {child.name}: meta={record.checksum} raw={raw_sha256}"
                )

            bronze_id = child.name
            records.append(
                ArchiveRecordEntry(
                    bronze_id=bronze_id,
                    source_uri=record.source_uri,
                    source_format=record.source_format,
                    structure_class=str(record.structure_class),
                    checksum=record.checksum,
                    archive_path=f"bronze/{bronze_id}/raw",
                    meta_path=f"bronze/{bronze_id}/meta.json",
                    raw_sha256=raw_sha256,
                    raw_byte_count=len(raw_bytes),
                )
            )

        return ArchiveManifest(
            archive_format_version=ARCHIVE_FORMAT_VERSION,
            formaforge_version=__version__,
            packed_at=datetime.now(UTC),
            source_storage_dir=str(storage_dir),
            records=records,
        )
