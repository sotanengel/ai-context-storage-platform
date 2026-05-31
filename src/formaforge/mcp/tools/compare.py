"""MCP tool: compare_formats."""

import json

from formaforge.gold.materializer import GoldMaterializer
from formaforge.models.gold import GoldRequest
from formaforge.silver.cdm_parser import CdmParser


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
    doc = CdmParser().parse(silver_cdm_text)
    adapters: list[str] = json.loads(adapter_names)
    materializer = GoldMaterializer()
    results = []
    for name in adapters:
        try:
            request = GoldRequest(silver_id=silver_id, adapter_name=name)
            result = materializer.materialize(doc, request)
            results.append(
                {
                    "adapter": name,
                    "text": result.text,
                    "byte_count": result.byte_count,
                    "token_estimate": result.token_estimate,
                    "error": None,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "adapter": name,
                    "text": None,
                    "byte_count": 0,
                    "token_estimate": 0,
                    "error": str(exc),
                }
            )
    return json.dumps(results)
