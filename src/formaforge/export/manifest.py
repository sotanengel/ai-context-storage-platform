"""Archive manifest models for Bronze pack exports."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

ARCHIVE_FORMAT_VERSION = "1.0"


class ArchiveRecordEntry(BaseModel):
    bronze_id: str
    source_uri: str
    source_format: str
    structure_class: str
    checksum: str
    archive_path: str
    meta_path: str
    raw_sha256: str
    raw_byte_count: int


class ArchiveManifest(BaseModel):
    archive_format_version: str = ARCHIVE_FORMAT_VERSION
    formaforge_version: str
    packed_at: datetime
    source_storage_dir: str
    records: list[ArchiveRecordEntry] = Field(default_factory=list)

    @property
    def record_count(self) -> int:
        return len(self.records)

    def file_tree_lines(self) -> list[str]:
        lines = ["manifest.json", "FORMAFORGE_AI_RESTORE_GUIDE.md", "bronze/"]
        for entry in sorted(self.records, key=lambda r: r.bronze_id):
            lines.append(f"  {entry.bronze_id}/")
            lines.append("    meta.json")
            lines.append("    raw")
        return lines
