"""MCP tool: normalize_to_silver."""

from formaforge.models.bronze import BronzeRecord, StructureClass
from formaforge.models.silver import ConversionMethod
from formaforge.silver.cdm_writer import CdmWriter
from formaforge.silver.normalizer import SilverNormalizer


def normalize_to_silver(
    bronze_id: str,
    raw_content_path: str,
    source_format: str,
    source_uri: str,
    structure_class: str,
    conversion_method: str = "auto",
) -> str:
    """Normalize a Bronze record to Canonical Markdown (CDM).

    Args:
        bronze_id: ID of the Bronze record.
        raw_content_path: Filesystem path to the raw content file.
        source_format: Detected format (json, csv, xml, …).
        source_uri: Original data URI.
        structure_class: 'structured' or 'unstructured'.
        conversion_method: 'auto', 'deterministic', or 'ai'.

    Returns:
        CDM Markdown string.
    """
    record = BronzeRecord(
        id=bronze_id,
        source_uri=source_uri,
        source_format=source_format,
        structure_class=StructureClass(structure_class),
        checksum=bronze_id,
        raw_content_path=raw_content_path,
    )
    method = ConversionMethod(conversion_method)
    normalizer = SilverNormalizer()
    doc = normalizer.normalize(record, conversion_method=method)
    return CdmWriter().write(doc)
