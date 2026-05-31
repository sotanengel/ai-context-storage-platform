"""Tests for structure class detection."""

import json

import pytest
import yaml

from formaforge.bronze.detector import StructureClassifier
from formaforge.models.bronze import StructureClass


@pytest.fixture()
def classifier() -> StructureClassifier:
    return StructureClassifier()


def test_detect_json(classifier: StructureClassifier) -> None:
    content = json.dumps({"key": "value", "num": 42}).encode()
    assert classifier.classify(content, "data.json") == StructureClass.STRUCTURED


def test_detect_jsonl(classifier: StructureClassifier) -> None:
    content = b'{"a": 1}\n{"b": 2}\n'
    assert classifier.classify(content, "data.jsonl") == StructureClass.STRUCTURED


def test_detect_yaml(classifier: StructureClassifier) -> None:
    content = yaml.dump({"key": "value"}).encode()
    assert classifier.classify(content, "config.yaml") == StructureClass.STRUCTURED


def test_detect_csv(classifier: StructureClassifier) -> None:
    content = b"name,age,city\nAlice,30,Tokyo\nBob,25,Osaka\n"
    assert classifier.classify(content, "data.csv") == StructureClass.STRUCTURED


def test_detect_xml(classifier: StructureClassifier) -> None:
    content = b"<?xml version='1.0'?><root><item>value</item></root>"
    assert classifier.classify(content, "data.xml") == StructureClass.STRUCTURED


def test_detect_toml(classifier: StructureClassifier) -> None:
    content = b'[section]\nkey = "value"\nnum = 42\n'
    assert classifier.classify(content, "config.toml") == StructureClass.STRUCTURED


def test_detect_markdown(classifier: StructureClassifier) -> None:
    content = b"# Heading\n\nSome **bold** text.\n"
    assert classifier.classify(content, "doc.md") == StructureClass.STRUCTURED


def test_detect_plain_text(classifier: StructureClassifier) -> None:
    content = b"This is just some plain text without any structure."
    assert classifier.classify(content, "notes.txt") == StructureClass.UNSTRUCTURED


def test_detect_by_extension_overrides_content(classifier: StructureClassifier) -> None:
    content = b'{"key": "value"}'
    assert classifier.classify(content, "data.json") == StructureClass.STRUCTURED


def test_detect_no_filename_falls_back_to_content(classifier: StructureClassifier) -> None:
    content = json.dumps({"a": 1}).encode()
    result = classifier.classify(content, None)
    assert result == StructureClass.STRUCTURED


def test_detect_binary_pdf_header(classifier: StructureClassifier) -> None:
    content = b"%PDF-1.4 fake content"
    result = classifier.classify(content, "doc.pdf")
    assert result == StructureClass.UNSTRUCTURED
