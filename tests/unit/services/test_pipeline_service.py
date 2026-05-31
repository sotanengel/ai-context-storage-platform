"""Tests for PipelineService."""

from pathlib import Path

import pytest

from formaforge.models.gold import DataShape, GoldRequest, Objective, UseCase
from formaforge.models.silver import CdmDocument, CdmFrontmatter, CdmTableBlock
from formaforge.services.pipeline import create_pipeline_service

_SAMPLE_CDM = """\
---
source_format: json
source_uri: test.json
structure_class: structured
cdm_schema_version: "2.0"
conversion_method: deterministic
conversion_confidence: 1.0
pii_flags: []
---

# Products

```table
columns: [id:int, name:str]
rows:
  - [1, Widget]
```
"""


@pytest.fixture()
def service(tmp_path: Path):
    return create_pipeline_service(storage_dir=tmp_path / "bronze")


def test_ingest_and_normalize_by_id(service) -> None:
    record = service.ingest(
        source_uri="s3://test/data.json",
        content=b'[{"id": 1, "name": "Alice"}]',
        filename="data.json",
    )
    doc = service.normalize(record.id)
    assert doc.frontmatter.source_format == "json"
    assert len(doc.blocks) == 1

    text = service.normalize_to_text(record.id)
    assert "cdm_schema_version" in text


def test_normalize_missing_bronze_raises(service) -> None:
    with pytest.raises(ValueError, match="Bronze record not found"):
        service.normalize("nonexistent-id")


def test_materialize_from_text(service) -> None:
    request = GoldRequest(silver_id="s1", adapter_name="yaml")
    result = service.materialize_from_text(_SAMPLE_CDM, request)
    assert result.adapter_name == "yaml"
    assert "Widget" in result.text
    assert result.byte_count > 0


def test_compare_adapters(service) -> None:
    fm = CdmFrontmatter(source_format="json", source_uri="", structure_class="structured")
    doc = CdmDocument(frontmatter=fm, title="T")
    results = service.compare_adapters(doc, "s1", ["yaml", "nonexistent_adapter_xyz"])
    assert len(results) == 2
    assert results[0]["error"] is None
    assert results[1]["error"] is not None


def test_benchmark_adapters(service) -> None:
    doc = service.parse_cdm(_SAMPLE_CDM)
    results = service.benchmark_adapters(doc, "s1", ["yaml"])
    assert len(results) == 1
    assert results[0].adapter == "yaml"
    assert results[0].latency_ms >= 0
    assert results[0].fidelity_score > 0.0
    assert results[0].error is None


def test_recommend(service) -> None:
    result = service.recommend(
        use_case=UseCase.PROMPT_CONTEXT,
        data_shape=DataShape.NESTED,
        objective=Objective.ACCURACY,
    )
    assert result["format"] == "yaml"
    assert "rationale" in result


def test_parse_cdm_table_block(service) -> None:
    doc = service.parse_cdm(_SAMPLE_CDM)
    table_blocks = [b for b in doc.blocks if isinstance(b, CdmTableBlock)]
    assert len(table_blocks) == 1


def test_list_adapters(service) -> None:
    adapters = service.list_adapters()
    names = [a["name"] for a in adapters]
    assert "yaml" in names
    assert "json" in names
