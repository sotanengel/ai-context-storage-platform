"""Tests for YAML, CSV, XML, TOML, Markdown converters."""

import pytest

from formaforge.models.silver import CdmDataBlock, CdmTableBlock
from formaforge.silver.cdm_parser import CdmParser
from formaforge.silver.cdm_writer import CdmWriter
from formaforge.silver.converters.csv_converter import CsvConverter
from formaforge.silver.converters.markdown_converter import MarkdownConverter
from formaforge.silver.converters.toml_converter import TomlConverter
from formaforge.silver.converters.xml_converter import XmlConverter
from formaforge.silver.converters.yaml_converter import YamlConverter

# ── YAML ────────────────────────────────────────────────────────────────────


@pytest.fixture()
def yaml_conv() -> YamlConverter:
    return YamlConverter()


YAML_LIST = """\
- id: 1
  name: Alice
  score: 95.5
- id: 2
  name: Bob
  score: 88.0
"""

YAML_NESTED = """\
customer:
  id: 123
  name: Alice
  tags:
    - vip
    - active
"""


def test_yaml_uniform_list_produces_table(yaml_conv: YamlConverter) -> None:
    doc = yaml_conv.convert(YAML_LIST, "config.yaml")
    table_blocks = [b for b in doc.blocks if isinstance(b, CdmTableBlock)]
    assert len(table_blocks) == 1
    assert len(table_blocks[0].rows) == 2


def test_yaml_nested_produces_data_block(yaml_conv: YamlConverter) -> None:
    doc = yaml_conv.convert(YAML_NESTED, "config.yaml")
    data_blocks = [b for b in doc.blocks if isinstance(b, CdmDataBlock)]
    assert len(data_blocks) == 1


def test_yaml_roundtrip(yaml_conv: YamlConverter) -> None:
    doc = yaml_conv.convert(YAML_LIST, "config.yaml")
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    tb = next(b for b in recovered.blocks if isinstance(b, CdmTableBlock))
    assert tb.rows[0][1] == "Alice"


# ── CSV ─────────────────────────────────────────────────────────────────────


@pytest.fixture()
def csv_conv() -> CsvConverter:
    return CsvConverter()


CSV_DATA = "order_id,region,amount\n1001,APAC,12000.00\n1002,EMEA,8400.50\n"


def test_csv_produces_table_block(csv_conv: CsvConverter) -> None:
    doc = csv_conv.convert(CSV_DATA, "data.csv")
    table_blocks = [b for b in doc.blocks if isinstance(b, CdmTableBlock)]
    assert len(table_blocks) == 1
    assert len(table_blocks[0].rows) == 2


def test_csv_columns_include_names(csv_conv: CsvConverter) -> None:
    doc = csv_conv.convert(CSV_DATA, "data.csv")
    tb = next(b for b in doc.blocks if isinstance(b, CdmTableBlock))
    col_names = [c.split(":")[0] for c in tb.columns]
    assert "order_id" in col_names
    assert "region" in col_names


def test_csv_roundtrip(csv_conv: CsvConverter) -> None:
    doc = csv_conv.convert(CSV_DATA, "data.csv")
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    tb = next(b for b in recovered.blocks if isinstance(b, CdmTableBlock))
    assert tb.rows[0][1] == "APAC"


# ── XML ─────────────────────────────────────────────────────────────────────


@pytest.fixture()
def xml_conv() -> XmlConverter:
    return XmlConverter()


XML_DATA = """\
<?xml version="1.0"?>
<orders>
  <order><id>1001</id><region>APAC</region><amount>12000.00</amount></order>
  <order><id>1002</id><region>EMEA</region><amount>8400.50</amount></order>
</orders>
"""

XML_NESTED = """\
<?xml version="1.0"?>
<customer>
  <id>123</id>
  <profile>
    <name>Alice</name>
    <email>alice@example.com</email>
  </profile>
</customer>
"""


def test_xml_uniform_children_produces_table(xml_conv: XmlConverter) -> None:
    doc = xml_conv.convert(XML_DATA, "data.xml")
    table_blocks = [b for b in doc.blocks if isinstance(b, CdmTableBlock)]
    assert len(table_blocks) == 1


def test_xml_nested_produces_data_block(xml_conv: XmlConverter) -> None:
    doc = xml_conv.convert(XML_NESTED, "data.xml")
    data_blocks = [b for b in doc.blocks if isinstance(b, CdmDataBlock)]
    assert len(data_blocks) == 1


def test_xml_source_format(xml_conv: XmlConverter) -> None:
    doc = xml_conv.convert(XML_DATA, "data.xml")
    assert doc.frontmatter.source_format == "xml"


# ── TOML ────────────────────────────────────────────────────────────────────


@pytest.fixture()
def toml_conv() -> TomlConverter:
    return TomlConverter()


TOML_DATA = """\
[server]
host = "localhost"
port = 8080

[database]
url = "sqlite:///app.db"
pool_size = 5
"""


def test_toml_produces_data_block(toml_conv: TomlConverter) -> None:
    doc = toml_conv.convert(TOML_DATA, "config.toml")
    data_blocks = [b for b in doc.blocks if isinstance(b, CdmDataBlock)]
    assert len(data_blocks) == 1


def test_toml_roundtrip(toml_conv: TomlConverter) -> None:
    doc = toml_conv.convert(TOML_DATA, "config.toml")
    text = CdmWriter().write(doc)
    recovered = CdmParser().parse(text)
    db = next(b for b in recovered.blocks if isinstance(b, CdmDataBlock))
    assert isinstance(db.content, dict)
    assert "server" in db.content


# ── Markdown ────────────────────────────────────────────────────────────────


@pytest.fixture()
def md_conv() -> MarkdownConverter:
    return MarkdownConverter()


MD_DATA = """\
# My Document

Some introductory text.

## Section 1

Content here.
"""


def test_markdown_preserves_body(md_conv: MarkdownConverter) -> None:
    doc = md_conv.convert(MD_DATA, "doc.md")
    assert "My Document" in doc.title or "My Document" in doc.body


def test_markdown_source_format(md_conv: MarkdownConverter) -> None:
    doc = md_conv.convert(MD_DATA, "doc.md")
    assert doc.frontmatter.source_format == "markdown"


def test_markdown_with_existing_frontmatter(md_conv: MarkdownConverter) -> None:
    text = """\
---
title: Existing Doc
author: Alice
---

# Body

Content.
"""
    doc = md_conv.convert(text, "doc.md")
    assert doc.frontmatter.source_format == "markdown"
