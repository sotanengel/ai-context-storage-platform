"""Gold materializer: convert CdmDocument to the optimal output format."""

from formaforge.gold.adapters import AdapterRegistry
from formaforge.gold.policy import PolicyEngine
from formaforge.gold.token_counter import TokenCounter
from formaforge.models.gold import GoldRequest, GoldResult
from formaforge.models.silver import CdmDocument

# Backward-compatible alias used by register_format_adapter tool
_ADAPTERS = AdapterRegistry.instance()._adapters


class GoldMaterializer:
    def __init__(self) -> None:
        self._policy = PolicyEngine()
        self._registry = AdapterRegistry.instance()
        self._token_counter = TokenCounter()

    def materialize(self, doc: CdmDocument, request: GoldRequest) -> GoldResult:
        adapter_name = request.adapter_name or self._policy.recommend(
            use_case=request.use_case,
            data_shape=request.data_shape,
            target_model=request.target_model,
            objective=request.objective,
        )
        adapter = self._registry.get(adapter_name)
        if not adapter:
            raise ValueError(f"Unknown adapter: {adapter_name!r}")

        text = adapter.render(doc, **request.options)
        token_estimate = self._token_counter.count(text, str(request.target_model))

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
            {"name": name, "class": type(adapter).__name__}
            for name, adapter in self._registry.all().items()
        ]
