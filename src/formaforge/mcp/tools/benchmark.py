"""MCP tool: benchmark_format."""

import json
import time

from formaforge.gold.materializer import GoldMaterializer
from formaforge.models.gold import GoldRequest
from formaforge.silver.cdm_parser import CdmParser


def benchmark_format(
    silver_cdm_text: str,
    silver_id: str,
    adapter_names: str,
) -> str:
    """Benchmark multiple Gold adapters on the same CDM document.

    Args:
        silver_cdm_text: CDM Markdown string.
        silver_id: Source Silver record ID.
        adapter_names: JSON array of adapter names.

    Returns:
        JSON array with per-adapter latency_ms, byte_count, token_estimate.
    """
    doc = CdmParser().parse(silver_cdm_text)
    adapters: list[str] = json.loads(adapter_names)
    materializer = GoldMaterializer()
    results = []
    for name in adapters:
        try:
            request = GoldRequest(silver_id=silver_id, adapter_name=name)
            t0 = time.perf_counter()
            result = materializer.materialize(doc, request)
            latency_ms = (time.perf_counter() - t0) * 1000
            results.append(
                {
                    "adapter": name,
                    "latency_ms": round(latency_ms, 2),
                    "byte_count": result.byte_count,
                    "token_estimate": result.token_estimate,
                    "error": None,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "adapter": name,
                    "latency_ms": 0,
                    "byte_count": 0,
                    "token_estimate": 0,
                    "error": str(exc),
                }
            )
    return json.dumps(results)
