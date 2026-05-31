"""Silver layer data models (Canonical Document Model)."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ConversionMethod(StrEnum):
    DETERMINISTIC = "deterministic"
    AI = "ai"
    AUTO = "auto"


class CdmFrontmatter(BaseModel):
    source_format: str
    source_uri: str
    structure_class: str
    normalized_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    conversion_method: ConversionMethod = ConversionMethod.DETERMINISTIC
    conversion_confidence: float = 1.0
    cdm_schema_version: str = "2.0"
    pii_flags: list[str] = Field(default_factory=list)


class CdmTableBlock(BaseModel):
    kind: str = "table"
    columns: list[str]
    rows: list[list[Any]]


class CdmDataBlock(BaseModel):
    kind: str = "data"
    content: dict[str, Any] | list[Any]


CdmBlock = CdmTableBlock | CdmDataBlock


class CdmDocument(BaseModel):
    frontmatter: CdmFrontmatter
    title: str = ""
    body: str = ""
    blocks: list[CdmBlock] = Field(default_factory=list)
