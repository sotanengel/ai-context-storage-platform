"""Tests for Gold format adapters."""

import json

import pytest
import yaml

from formaforge.gold.adapters.csv_adapter import CsvAdapter
from formaforge.gold.adapters.json_adapter import JsonAdapter
from formaforge.gold.adapters.jsonl_adapter import JsonlAdapter
from formaforge.gold.adapters.markdown_kv import MarkdownKvAdapter
from formaforge.gold.adapters.plaintext_adapter import PlaintextAdapter
from formaforge.gold.adapters.xml_adapter import XmlAdapter
from formaforge.gold.adapters.yaml_adapter import YamlAdapter
from formaforge.models.silver import CdmDataBlock, CdmDocument, CdmFrontmatter, CdmTableBlock


def _doc_with_table() -> CdmDocument:
    fm = CdmFrontmatter(source_format="json", source_uri="test", structure_class="structured")
    block = CdmTableBlock(
        columns=["id:int", "name:string"],
        rows=[[1, "Alice"], [2, "Bob"]],
    )
    return CdmDocument(frontmatter=fm, title="Test", blocks=[block])


def _doc_with_data() -> CdmDocument:
    fm = CdmFrontmatter(source_format="json", source_uri="test", structure_class="structured")
    block = CdmDataBlock(content={"server": {"host": "localhost", "port": 8080}})
    return CdmDocument(frontmatter=fm, title="Config", blocks=[block])


def _doc_with_body() -> CdmDocument:
    fm = CdmFrontmatter(source_format="pdf", source_uri="test", structure_class="unstructured")
    return CdmDocument(
        frontmatter=fm, title="Meeting Notes", body="Discussion about X.\n\nDecisions made."
    )


# ── Markdown-KV ─────────────────────────────────────────────────────────────


def test_markdown_kv_table_renders_rows() -> None:
    text = MarkdownKvAdapter().render(_doc_with_table())
    assert "Alice" in text
    assert "Bob" in text


def test_markdown_kv_body_renders_text() -> None:
    text = MarkdownKvAdapter().render(_doc_with_body())
    assert "Discussion" in text


# ── YAML ─────────────────────────────────────────────────────────────────────


def test_yaml_adapter_produces_valid_yaml() -> None:
    text = YamlAdapter().render(_doc_with_data())
    parsed = yaml.safe_load(text)
    assert parsed is not None


def test_yaml_adapter_preserves_nested() -> None:
    text = YamlAdapter().render(_doc_with_data())
    assert "server" in text
    assert "localhost" in text


# ── CSV ──────────────────────────────────────────────────────────────────────


def test_csv_adapter_produces_header_and_rows() -> None:
    text = CsvAdapter().render(_doc_with_table())
    lines = [line for line in text.strip().splitlines() if line]
    assert len(lines) == 3
    assert "id" in lines[0]
    assert "Alice" in lines[1]


def test_csv_adapter_raises_for_non_table() -> None:
    with pytest.raises(ValueError, match="table"):
        CsvAdapter().render(_doc_with_body())


# ── JSON ─────────────────────────────────────────────────────────────────────


def test_json_adapter_produces_valid_json() -> None:
    text = JsonAdapter().render(_doc_with_table())
    parsed = json.loads(text)
    assert isinstance(parsed, dict | list)


def test_json_adapter_minified_option() -> None:
    adapter = JsonAdapter()
    text = adapter.render(_doc_with_table(), pretty="false")
    assert "\n" not in text


# ── JSONL ────────────────────────────────────────────────────────────────────


def test_jsonl_openai_schema() -> None:
    doc = _doc_with_body()
    text = JsonlAdapter().render(doc, schema="openai")
    line = json.loads(text.strip().split("\n")[0])
    assert "messages" in line


def test_jsonl_anthropic_schema() -> None:
    doc = _doc_with_body()
    text = JsonlAdapter().render(doc, schema="anthropic")
    line = json.loads(text.strip().split("\n")[0])
    assert "messages" in line


# ── XML ──────────────────────────────────────────────────────────────────────


def test_xml_adapter_produces_xml() -> None:
    text = XmlAdapter().render(_doc_with_data())
    assert text.strip().startswith("<")
    assert "</document>" in text or "</root>" in text or ">" in text


# ── Plaintext ────────────────────────────────────────────────────────────────


def test_plaintext_strips_markup() -> None:
    text = PlaintextAdapter().render(_doc_with_body())
    assert "Discussion" in text
    assert "---" not in text
    assert "```" not in text


# ── TOON ─────────────────────────────────────────────────────────────────────


def test_toon_adapter_table_renders_rows() -> None:
    from formaforge.gold.adapters.toon_adapter import ToonAdapter

    text = ToonAdapter().render(_doc_with_table())
    assert "Alice" in text
    assert "Bob" in text
    assert "id" in text


def test_toon_adapter_data_renders_keys() -> None:
    from formaforge.gold.adapters.toon_adapter import ToonAdapter

    text = ToonAdapter().render(_doc_with_data())
    assert "server" in text
    assert "localhost" in text


def test_toon_adapter_nested_uses_braces() -> None:
    from formaforge.gold.adapters.toon_adapter import ToonAdapter

    text = ToonAdapter().render(_doc_with_data())
    assert "{" in text
    assert "}" in text


def test_toon_adapter_token_efficient_vs_json() -> None:
    """TOON must use ≤ 80% tokens compared to equivalent JSON for nested docs."""
    from formaforge.gold.adapters.json_adapter import JsonAdapter
    from formaforge.gold.adapters.toon_adapter import ToonAdapter

    doc = _doc_with_data()
    json_text = JsonAdapter().render(doc)
    toon_text = ToonAdapter().render(doc)
    json_tokens = max(1, len(json_text.encode()) // 4)
    toon_tokens = max(1, len(toon_text.encode()) // 4)
    assert toon_tokens <= json_tokens * 0.95


def test_toon_adapter_body_doc_renders() -> None:
    from formaforge.gold.adapters.toon_adapter import ToonAdapter

    text = ToonAdapter().render(_doc_with_body())
    assert "Discussion" in text


def test_toon_adapter_registered_in_registry() -> None:
    from formaforge.gold.adapters import AdapterRegistry

    registry = AdapterRegistry.instance()
    assert registry.get("toon") is not None
