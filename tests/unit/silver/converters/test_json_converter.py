"""Tests for JSON → CDM deterministic converter."""

import json

import pytest

from formaforge.models.silver import CdmDataBlock, CdmTableBlock
from formaforge.silver.cdm_parser import CdmParser
from formaforge.silver.cdm_writer import CdmWriter
from formaforge.silver.converters.json_converter import JsonConverter


@pytest.fixture()
def converter() -> JsonConverter:
    return JsonConverter()


UNIFORM_ARRAY = json.dumps(
    [
        {"id": 1, "name": "Alice", "score": 95.5},
        {"id": 2, "name": "Bob", "score": 88.0},
    ]
)

NESTED_OBJECT = json.dumps(
    {
        "customer": {"id": 123, "name": "Alice", "tags": ["vip", "active"]},
        "region": "APAC",
    }
)

SCALAR_TOP_LEVEL = json.dumps({"title": "Report", "version": 2, "active": True})


def test_uniform_array_produces_table_block(converter: JsonConverter) -> None:
    doc = converter.convert(UNIFORM_ARRAY, "test.json")
    table_blocks = [b for b in doc.blocks if isinstance(b, CdmTableBlock)]
    assert len(table_blocks) == 1
    assert len(table_blocks[0].rows) == 2


def test_uniform_array_columns_include_types(converter: JsonConverter) -> None:
    doc = converter.convert(UNIFORM_ARRAY, "test.json")
    tb = next(b for b in doc.blocks if isinstance(b, CdmTableBlock))
    col_names = [c.split(":")[0] for c in tb.columns]
    assert "id" in col_names
    assert "name" in col_names
    assert "score" in col_names


def test_nested_object_produces_data_block(converter: JsonConverter) -> None:
    doc = converter.convert(NESTED_OBJECT, "test.json")
    data_blocks = [b for b in doc.blocks if isinstance(b, CdmDataBlock)]
    assert len(data_blocks) == 1


def test_scalar_values_go_to_frontmatter_or_body(converter: JsonConverter) -> None:
    doc = converter.convert(SCALAR_TOP_LEVEL, "test.json")
    cdm_text = CdmWriter().write(doc)
    assert "title" in cdm_text or "Report" in cdm_text


def test_roundtrip_uniform_array(converter: JsonConverter) -> None:
    doc = converter.convert(UNIFORM_ARRAY, "test.json")
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    tb = next(b for b in recovered.blocks if isinstance(b, CdmTableBlock))
    assert tb.rows[0][1] == "Alice"
    assert tb.rows[1][1] == "Bob"


def test_roundtrip_nested_object(converter: JsonConverter) -> None:
    doc = converter.convert(NESTED_OBJECT, "test.json")
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    db = next(b for b in recovered.blocks if isinstance(b, CdmDataBlock))
    assert db.content["customer"]["id"] == 123  # type: ignore[index]


def test_source_format_is_json(converter: JsonConverter) -> None:
    doc = converter.convert(UNIFORM_ARRAY, "test.json")
    assert doc.frontmatter.source_format == "json"


def test_conversion_method_is_deterministic(converter: JsonConverter) -> None:
    doc = converter.convert(UNIFORM_ARRAY, "test.json")
    assert doc.frontmatter.conversion_method == "deterministic"
    assert doc.frontmatter.conversion_confidence == 1.0
