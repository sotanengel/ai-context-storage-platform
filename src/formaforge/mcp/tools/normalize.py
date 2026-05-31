"""MCP tool: normalize_to_silver."""

from pathlib import Path

from formaforge.models.silver import ConversionMethod
from formaforge.services.pipeline import create_pipeline_service


def normalize_to_silver(
    bronze_id: str,
    storage_dir: str | None = None,
    conversion_method: str = "auto",
) -> str:
    """Normalize a Bronze record to Canonical Markdown (CDM).

    Args:
        bronze_id: ID of the Bronze record (from ingest_to_bronze).
        storage_dir: Bronze storage directory used during ingest (optional).
        conversion_method: 'auto', 'deterministic', or 'ai'.

    Returns:
        CDM Markdown string.
    """
    storage = Path(storage_dir) if storage_dir else None
    service = create_pipeline_service(storage_dir=storage)
    method = ConversionMethod(conversion_method)
    return service.normalize_to_text(bronze_id, conversion_method=method)
