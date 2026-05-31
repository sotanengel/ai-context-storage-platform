"""Integration: Silver → Gold materialization for all adapters."""

import json
from pathlib import Path

import pytest

from formaforge.bronze.ingester import BronzeIngester
from formaforge.gold.materializer import GoldMaterializer
from formaforge.models.gold import DataShape, GoldRequest, Objective, UseCase
from formaforge.silver.normalizer import SilverNormalizer


@pytest.fixture()
def ingester(tmp_path: Path) -> BronzeIngester:
    return BronzeIngester(storage_dir=tmp_path / "bronze")


@pytest.fixture()
def normalizer() -> SilverNormalizer:
    return SilverNormalizer()


@pytest.fixture()
def materializer() -> GoldMaterializer:
    return GoldMaterializer()


def test_json_array_to_yaml(
    ingester: BronzeIngester, normalizer: SilverNormalizer, materializer: GoldMaterializer
) -> None:
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    record = ingester.ingest("s3://test/data.json", json.dumps(data).encode(), "data.json")
    doc = normalizer.normalize(record)
    request = GoldRequest(
        silver_id=record.id,
        use_case=UseCase.PROMPT_CONTEXT,
        data_shape=DataShape.NESTED,
        objective=Objective.ACCURACY,
        adapter_name="yaml",
    )
    result = materializer.materialize(doc, request)
    assert "Alice" in result.text
    assert result.adapter_name == "yaml"
    assert result.token_estimate > 0


def test_csv_to_csv_adapter(
    ingester: BronzeIngester, normalizer: SilverNormalizer, materializer: GoldMaterializer
) -> None:
    csv_data = b"col1,col2\nfoo,bar\nbaz,qux\n"
    record = ingester.ingest("s3://test/data.csv", csv_data, "data.csv")
    doc = normalizer.normalize(record)
    request = GoldRequest(
        silver_id=record.id,
        adapter_name="csv",
    )
    result = materializer.materialize(doc, request)
    assert "foo" in result.text
    assert "col1" in result.text


def test_policy_selects_adapter_when_none_specified(
    ingester: BronzeIngester, normalizer: SilverNormalizer, materializer: GoldMaterializer
) -> None:
    data = [{"x": 1, "y": 2}]
    record = ingester.ingest("s3://test/data.json", json.dumps(data).encode(), "data.json")
    doc = normalizer.normalize(record)
    request = GoldRequest(
        silver_id=record.id,
        use_case=UseCase.PROMPT_CONTEXT,
        data_shape=DataShape.NESTED,
        objective=Objective.ACCURACY,
    )
    result = materializer.materialize(doc, request)
    assert result.adapter_name != ""
    assert len(result.text) > 0
