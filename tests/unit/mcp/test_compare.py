"""Tests for compare_formats MCP tool."""

import json

from formaforge.mcp.tools.compare import compare_formats

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

# Items

```table columns=[id:int,label:str]
rows:
- [1, alpha]
- [2, beta]
```
"""


def test_compare_returns_list() -> None:
    result = compare_formats(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="s1",
        adapter_names=json.dumps(["yaml", "json"]),
    )
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 2


def test_compare_item_fields() -> None:
    result = compare_formats(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="s1",
        adapter_names=json.dumps(["yaml"]),
    )
    parsed = json.loads(result)
    item = parsed[0]
    assert "adapter_name" in item
    assert "byte_count" in item
    assert "token_estimate" in item
    assert "text" in item


def test_compare_invalid_adapter() -> None:
    result = compare_formats(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="s1",
        adapter_names=json.dumps(["nonexistent_xyz"]),
    )
    parsed = json.loads(result)
    assert parsed[0].get("error") is not None


def test_compare_multiple_adapters_distinct_output() -> None:
    result = compare_formats(
        silver_cdm_text=_SAMPLE_CDM,
        silver_id="s1",
        adapter_names=json.dumps(["yaml", "json", "csv"]),
    )
    parsed = json.loads(result)
    assert len(parsed) == 3
    names = [p["adapter_name"] for p in parsed if p.get("error") is None]
    assert len(set(names)) == len(names)
