"""Tests for MCP server tool registration."""

import json
from pathlib import Path

from formaforge.mcp.server import create_server


def test_server_creates_successfully() -> None:
    server = create_server()
    assert server is not None


def test_server_has_name() -> None:
    server = create_server()
    assert server.name == "formaforge"


def test_ingest_tool_called_returns_json(tmp_path: Path) -> None:
    import base64

    from formaforge.mcp.tools.ingest import ingest_to_bronze

    content = base64.b64encode(b'{"x": 1}').decode()
    result = ingest_to_bronze(
        source_uri="s3://test/data.json",
        content_b64=content,
        filename="data.json",
        storage_dir=str(tmp_path / "bronze"),
    )
    parsed = json.loads(result)
    assert "id" in parsed
    assert parsed["source_format"] == "json"


def test_list_formats_returns_adapters() -> None:
    from formaforge.mcp.tools.list_formats import list_formats

    result = list_formats()
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    names = [a["name"] for a in parsed]
    assert "yaml" in names
    assert "csv" in names
    assert "json" in names


def test_recommend_format_returns_adapter_name() -> None:
    from formaforge.mcp.tools.recommend import recommend_format

    result = recommend_format(
        use_case="prompt_context",
        data_shape="nested",
        target_model="generic",
        objective="accuracy",
    )
    parsed = json.loads(result)
    assert "format" in parsed
    assert parsed["format"] == "yaml"


def test_normalize_then_materialize(tmp_path: Path) -> None:
    import base64

    from formaforge.mcp.tools.ingest import ingest_to_bronze
    from formaforge.mcp.tools.materialize import materialize_gold
    from formaforge.mcp.tools.normalize import normalize_to_silver

    storage_dir = str(tmp_path / "bronze")
    content = base64.b64encode(b'[{"id": 1, "val": "hello"}]').decode()
    ingest_result = json.loads(
        ingest_to_bronze("s3://test/data.json", content, "data.json", storage_dir=storage_dir)
    )
    bronze_id = ingest_result["id"]
    raw_path = ingest_result["raw_content_path"]

    silver_text = normalize_to_silver(
        bronze_id=bronze_id,
        raw_content_path=raw_path,
        source_format="json",
        source_uri="s3://test/data.json",
        structure_class="structured",
    )
    assert "cdm_schema_version" in silver_text

    gold_result = json.loads(
        materialize_gold(silver_cdm_text=silver_text, silver_id=bronze_id, adapter_name="yaml")
    )
    assert "text" in gold_result
    assert "hello" in gold_result["text"]
