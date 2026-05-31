"""MCP tool: benchmark_format."""

import json
import time

from formaforge.gold.materializer import GoldMaterializer
from formaforge.models.gold import BenchmarkResult, GoldRequest
from formaforge.models.silver import CdmDocument, CdmTableBlock
from formaforge.silver.cdm_parser import CdmParser


def _fidelity_score(doc: CdmDocument, rendered: str) -> float:
    """Estimate structural fidelity of rendered output vs source CDM (0.0–1.0).

    Checks for presence of title, body text, and each table/data block.
    """
    checks: list[bool] = []

    if doc.title:
        checks.append(doc.title.lower() in rendered.lower())

    if doc.body.strip():
        first_word = doc.body.strip().split()[0].lower()
        checks.append(first_word in rendered.lower())

    for block in doc.blocks:
        if isinstance(block, CdmTableBlock) and block.columns:
            checks.append(block.columns[0].lower() in rendered.lower())
        else:
            checks.append(len(rendered) > 0)

    if not checks:
        return 1.0
    return sum(checks) / len(checks)


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
    doc = CdmParser().parse(silver_cdm_text)
    adapters: list[str] = json.loads(adapter_names)
    materializer = GoldMaterializer()
    results: list[dict[str, object]] = []

    for name in adapters:
        try:
            request = GoldRequest(silver_id=silver_id, adapter_name=name)
            t0 = time.perf_counter()
            result = materializer.materialize(doc, request)
            latency_ms = (time.perf_counter() - t0) * 1000
            fidelity = _fidelity_score(doc, result.text)
            bench = BenchmarkResult(
                adapter=name,
                latency_ms=round(latency_ms, 2),
                byte_count=result.byte_count,
                token_estimate=result.token_estimate,
                fidelity_score=round(fidelity, 4),
                error=None,
            )
        except Exception as exc:
            bench = BenchmarkResult(
                adapter=name,
                latency_ms=0.0,
                byte_count=0,
                token_estimate=0,
                fidelity_score=0.0,
                error=str(exc),
            )
        results.append(bench.model_dump())

    return json.dumps(results)
