"""MCP tool: ingest_to_bronze."""

import base64
import json
from pathlib import Path

from formaforge.bronze.ingester import BronzeIngester


def ingest_to_bronze(
    source_uri: str,
    content_b64: str,
    filename: str | None = None,
    storage_dir: str | None = None,
) -> str:
    """Ingest raw data into the Bronze layer.

    Args:
        source_uri: URI identifying the data source.
        content_b64: Base64-encoded raw content.
        filename: Optional filename hint for format detection.
        storage_dir: Optional override for Bronze storage directory.

    Returns:
        JSON string with BronzeRecord fields.
    """
    content = base64.b64decode(content_b64)
    storage = Path(storage_dir) if storage_dir else None
    ingester = BronzeIngester(storage_dir=storage)
    record = ingester.ingest(source_uri=source_uri, content=content, filename=filename)
    return json.dumps(record.model_dump(mode="json"), default=str)
