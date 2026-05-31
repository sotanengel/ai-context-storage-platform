"""MCP tool: materialize_gold."""

import json

from formaforge.gold.materializer import GoldMaterializer
from formaforge.models.gold import DataShape, GoldRequest, Objective, TargetModel, UseCase
from formaforge.silver.cdm_parser import CdmParser


def materialize_gold(
    silver_cdm_text: str,
    silver_id: str,
    adapter_name: str | None = None,
    use_case: str = "prompt_context",
    data_shape: str = "document",
    target_model: str = "generic",
    objective: str = "balance",
    options: str = "{}",
) -> str:
    """Materialize a CDM document in the specified or recommended Gold format.

    Args:
        silver_cdm_text: The CDM Markdown string to materialize.
        silver_id: ID of the source Silver record.
        adapter_name: Force a specific adapter (optional).
        use_case: Use case for auto-selection.
        data_shape: Data shape for auto-selection.
        target_model: Target model for auto-selection.
        objective: Optimization objective for auto-selection.
        options: JSON string of adapter options.

    Returns:
        JSON string with text, adapter_name, byte_count, token_estimate.
    """
    doc = CdmParser().parse(silver_cdm_text)
    opts = json.loads(options)
    request = GoldRequest(
        silver_id=silver_id,
        use_case=UseCase(use_case),
        data_shape=DataShape(data_shape),
        target_model=TargetModel(target_model),
        objective=Objective(objective),
        adapter_name=adapter_name,
        options={k: str(v) for k, v in opts.items()},
    )
    result = GoldMaterializer().materialize(doc, request)
    return json.dumps(result.model_dump())
