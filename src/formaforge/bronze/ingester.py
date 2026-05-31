"""Bronze ingestion service."""

from datetime import UTC, datetime
from pathlib import Path

from formaforge.bronze.checksums import sha256_of_bytes
from formaforge.bronze.detector import StructureClassifier
from formaforge.config import resolve_storage_dir
from formaforge.models.bronze import BronzeRecord


class BronzeIngester:
    def __init__(self, storage_dir: Path | None = None) -> None:
        self._storage = resolve_storage_dir(storage_dir)
        self._registry: dict[str, BronzeRecord] = {}
        self._classifier = StructureClassifier()

    def ingest(
        self,
        source_uri: str,
        content: bytes,
        filename: str | None = None,
    ) -> BronzeRecord:
        checksum = sha256_of_bytes(content)
        if checksum in self._registry:
            return self._registry[checksum]

        structure_class = self._classifier.classify(content, filename)
        source_format = self._classifier.detect_format(content, filename)

        record_id = checksum[:16]
        raw_path = self._persist(record_id, content)

        record = BronzeRecord(
            id=record_id,
            source_uri=source_uri,
            source_format=source_format,
            structure_class=structure_class,
            checksum=checksum,
            raw_content_path=str(raw_path),
            ingested_at=datetime.now(UTC),
        )
        self._registry[checksum] = record
        self._persist_metadata(record_id, record)
        return record

    def get_by_id(self, record_id: str) -> BronzeRecord | None:
        meta_path = self._storage / record_id / "meta.json"
        if not meta_path.exists():
            return None
        return BronzeRecord.model_validate_json(meta_path.read_text())

    def _persist(self, record_id: str, content: bytes) -> Path:
        dest_dir = self._storage / record_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        raw_path = dest_dir / "raw"
        raw_path.write_bytes(content)
        return raw_path

    def _persist_metadata(self, record_id: str, record: BronzeRecord) -> None:
        meta_path = self._storage / record_id / "meta.json"
        meta_path.write_text(record.model_dump_json(indent=2))
