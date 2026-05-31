"""MCP tool: benchmark_format."""

import json

from formaforge.services.pipeline import create_pipeline_service


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
        JSON array of BenchmarkResult objects with latency_ms, byte_count,
        token_estimate, fidelity_score, and error fields.
    """
    service = create_pipeline_service()
    doc = service.parse_cdm(silver_cdm_text)
    adapters: list[str] = json.loads(adapter_names)
    results = service.benchmark_adapters(doc, silver_id, adapters)
    return json.dumps([r.model_dump() for r in results])
