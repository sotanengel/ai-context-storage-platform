"""MCP tool: compare_formats."""

import json

from formaforge.services.pipeline import create_pipeline_service


def compare_formats(
    silver_cdm_text: str,
    silver_id: str,
    adapter_names: str,
) -> str:
    """Compare multiple Gold formats for the same CDM document.

    Args:
        silver_cdm_text: CDM Markdown string.
        silver_id: Source Silver record ID.
        adapter_names: JSON array of adapter names, e.g. '["yaml","csv","json"]'.

    Returns:
        JSON array with per-adapter text, byte_count, token_estimate.
    """
    service = create_pipeline_service()
    doc = service.parse_cdm(silver_cdm_text)
    adapters: list[str] = json.loads(adapter_names)
    results = service.compare_adapters(doc, silver_id, adapters)
    return json.dumps(results)
