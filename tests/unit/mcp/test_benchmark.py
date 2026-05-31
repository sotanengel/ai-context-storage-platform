"""Tests for benchmark_format MCP tool."""

import json

from formaforge.mcp.tools.benchmark import benchmark_format

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

```table columns=[id:int,name:str,price:float]
rows:
- [1, Widget, 9.99]
- [2, Gadget, 19.99]
```
"""


def test_benchmark_returns_list() -> None:
    result = benchmark_format(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="test-silver-1",
        adapter_names=json.dumps(["yaml", "json"]),
    )
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 2


def test_benchmark_fields_present() -> None:
    result = benchmark_format(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="test-silver-1",
        adapter_names=json.dumps(["yaml"]),
    )
    parsed = json.loads(result)
    item = parsed[0]
    assert item["adapter"] == "yaml"
    assert item["latency_ms"] >= 0
    assert item["byte_count"] > 0
    assert item["token_estimate"] > 0
    assert item["error"] is None
    assert "fidelity_score" in item
    assert 0.0 <= item["fidelity_score"] <= 1.0


def test_benchmark_invalid_adapter_has_error() -> None:
    result = benchmark_format(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="test-silver-1",
        adapter_names=json.dumps(["nonexistent_adapter_xyz"]),
    )
    parsed = json.loads(result)
    assert parsed[0]["error"] is not None


def test_benchmark_fidelity_table_doc() -> None:
    result = benchmark_format(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="test-silver-1",
        adapter_names=json.dumps(["yaml"]),
    )
    parsed = json.loads(result)
    assert parsed[0]["fidelity_score"] > 0.0


def test_benchmark_empty_adapters() -> None:
    result = benchmark_format(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="test-silver-1",
        adapter_names=json.dumps([]),
    )
    parsed = json.loads(result)
    assert parsed == []
