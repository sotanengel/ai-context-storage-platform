"""Gold materializer: convert CdmDocument to the optimal output format."""

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.gold.adapters.csv_adapter import CsvAdapter
from formaforge.gold.adapters.json_adapter import JsonAdapter
from formaforge.gold.adapters.jsonl_adapter import JsonlAdapter
from formaforge.gold.adapters.markdown_kv import MarkdownKvAdapter
from formaforge.gold.adapters.plaintext_adapter import PlaintextAdapter
from formaforge.gold.adapters.xml_adapter import XmlAdapter
from formaforge.gold.adapters.yaml_adapter import YamlAdapter
from formaforge.gold.policy import PolicyEngine
from formaforge.models.gold import GoldRequest, GoldResult
from formaforge.models.silver import CdmDocument

_ADAPTERS: dict[str, BaseAdapter] = {
    "markdown_kv": MarkdownKvAdapter(),
    "yaml": YamlAdapter(),
    "csv": CsvAdapter(),
    "json": JsonAdapter(),
    "jsonl": JsonlAdapter(),
    "xml": XmlAdapter(),
    "plaintext": PlaintextAdapter(),
}


class GoldMaterializer:
    def __init__(self) -> None:
        self._policy = PolicyEngine()

    def materialize(self, doc: CdmDocument, request: GoldRequest) -> GoldResult:
        adapter_name = request.adapter_name or self._policy.recommend(
            use_case=request.use_case,
            data_shape=request.data_shape,
            target_model=request.target_model,
            objective=request.objective,
        )
        adapter = _ADAPTERS.get(adapter_name)
        if not adapter:
            raise ValueError(f"Unknown adapter: {adapter_name!r}")

        text = adapter.render(doc, **request.options)
        token_estimate = adapter.estimate_tokens(text)

        return GoldResult(
            silver_id=request.silver_id,
            adapter_name=adapter_name,
            text=text,
            byte_count=len(text.encode()),
            token_estimate=token_estimate,
            options=request.options,
        )

    def list_adapters(self) -> list[dict[str, str]]:
        return [
            {"name": name, "class": type(adapter).__name__} for name, adapter in _ADAPTERS.items()
        ]
