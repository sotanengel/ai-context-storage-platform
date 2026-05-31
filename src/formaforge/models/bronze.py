"""Bronze layer data models."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class StructureClass(StrEnum):
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"


class BronzeRecord(BaseModel):
    id: str
    source_uri: str
    source_format: str
    structure_class: StructureClass
    checksum: str
    raw_content_path: str
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ingest_actor: str = "system"
    metadata: dict[str, str] = Field(default_factory=dict)
