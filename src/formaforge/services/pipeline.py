"""Pipeline service: orchestrates Bronze → Silver → Gold operations."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from formaforge.bronze.ingester import BronzeIngester
from formaforge.gold.adapters.base import BaseAdapter
from formaforge.gold.fidelity import fidelity_score
from formaforge.gold.materializer import GoldMaterializer
from formaforge.gold.policy import PolicyEngine
from formaforge.models.bronze import BronzeRecord
from formaforge.models.gold import (
    BenchmarkResult,
    DataShape,
    GoldRequest,
    GoldResult,
    Objective,
    TargetModel,
    UseCase,
)
from formaforge.models.silver import CdmDocument, ConversionMethod
from formaforge.silver.cdm_parser import CdmParser
from formaforge.silver.cdm_writer import CdmWriter
from formaforge.silver.normalizer import SilverNormalizer


class PipelineService:
    """Facade for ingest, normalize, and materialize pipeline operations."""

    def __init__(
        self,
        *,
        ingester: BronzeIngester | None = None,
        normalizer: SilverNormalizer | None = None,
        materializer: GoldMaterializer | None = None,
        policy: PolicyEngine | None = None,
        parser: CdmParser | None = None,
        writer: CdmWriter | None = None,
    ) -> None:
        self._ingester = ingester or BronzeIngester()
        self._normalizer = normalizer or SilverNormalizer()
        self._materializer = materializer or GoldMaterializer()
        self._policy = policy or PolicyEngine()
        self._parser = parser or CdmParser()
        self._writer = writer or CdmWriter()

    def ingest(
        self,
        source_uri: str,
        content: bytes,
        filename: str | None = None,
    ) -> BronzeRecord:
        return self._ingester.ingest(source_uri=source_uri, content=content, filename=filename)

    def normalize(
        self,
        bronze_id: str,
        *,
        conversion_method: ConversionMethod = ConversionMethod.AUTO,
    ) -> CdmDocument:
        record = self._ingester.get_by_id(bronze_id)
        if record is None:
            raise ValueError(f"Bronze record not found: {bronze_id!r}")
        return self._normalizer.normalize(record, conversion_method=conversion_method)

    def normalize_to_text(
        self,
        bronze_id: str,
        *,
        conversion_method: ConversionMethod = ConversionMethod.AUTO,
    ) -> str:
        doc = self.normalize(bronze_id, conversion_method=conversion_method)
        return self._writer.write(doc)

    def parse_cdm(self, text: str) -> CdmDocument:
        return self._parser.parse(text)

    def recommend(
        self,
        *,
        use_case: UseCase,
        data_shape: DataShape,
        target_model: TargetModel = TargetModel.GENERIC,
        objective: Objective = Objective.BALANCE,
    ) -> dict[str, str]:
        adapter = self._policy.recommend(
            use_case=use_case,
            data_shape=data_shape,
            target_model=target_model,
            objective=objective,
        )
        rationale = (
            f"For use_case={use_case.value!r}, data_shape={data_shape.value!r}, "
            f"objective={objective.value!r}: {adapter!r} selected per research-backed policy."
        )
        return {"format": adapter, "rationale": rationale}

    def materialize(self, doc: CdmDocument, request: GoldRequest) -> GoldResult:
        return self._materializer.materialize(doc, request)

    def materialize_from_text(self, cdm_text: str, request: GoldRequest) -> GoldResult:
        doc = self.parse_cdm(cdm_text)
        return self.materialize(doc, request)

    def compare_adapters(
        self,
        doc: CdmDocument,
        silver_id: str,
        names: list[str],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for name in names:
            try:
                request = GoldRequest(silver_id=silver_id, adapter_name=name)
                result = self._materializer.materialize(doc, request)
                results.append(
                    {
                        "adapter_name": name,
                        "text": result.text,
                        "byte_count": result.byte_count,
                        "token_estimate": result.token_estimate,
                        "error": None,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "adapter_name": name,
                        "text": None,
                        "byte_count": 0,
                        "token_estimate": 0,
                        "error": str(exc),
                    }
                )
        return results

    def benchmark_adapters(
        self,
        doc: CdmDocument,
        silver_id: str,
        names: list[str],
    ) -> list[BenchmarkResult]:
        results: list[BenchmarkResult] = []
        for name in names:
            try:
                request = GoldRequest(silver_id=silver_id, adapter_name=name)
                t0 = time.perf_counter()
                result = self._materializer.materialize(doc, request)
                latency_ms = (time.perf_counter() - t0) * 1000
                score = fidelity_score(doc, result.text)
                results.append(
                    BenchmarkResult(
                        adapter=name,
                        latency_ms=round(latency_ms, 2),
                        byte_count=result.byte_count,
                        token_estimate=result.token_estimate,
                        fidelity_score=round(score, 4),
                        error=None,
                    )
                )
            except Exception as exc:
                results.append(
                    BenchmarkResult(
                        adapter=name,
                        latency_ms=0.0,
                        byte_count=0,
                        token_estimate=0,
                        fidelity_score=0.0,
                        error=str(exc),
                    )
                )
        return results

    def list_adapters(self) -> list[dict[str, str]]:
        return self._materializer.list_adapters()

    def register_adapter(self, name: str, adapter: BaseAdapter) -> None:
        self._materializer.register_adapter(name, adapter)


def create_pipeline_service(storage_dir: Path | None = None) -> PipelineService:
    """Create a PipelineService with a shared BronzeIngester storage directory."""
    ingester = BronzeIngester(storage_dir=storage_dir)
    return PipelineService(ingester=ingester)
