"""MCP tool: materialize_gold."""

import json

from formaforge.models.gold import DataShape, GoldRequest, Objective, TargetModel, UseCase
from formaforge.services.pipeline import create_pipeline_service


def materialize_gold(
    silver_cdm_text: str,
    silver_id: str,
    adapter_name: str | None = None,
    use_case: str = "prompt_context",
    data_shape: str = "document",
    target_model: str = "generic",
    objective: str = "balance",
    pii_mask: str = "false",
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
        pii_mask: Set to "true" to replace PII entities with placeholders.
        options: JSON string of adapter options.

    Returns:
        JSON string with text, adapter_name, byte_count, token_estimate.
    """
    opts = json.loads(options)
    request = GoldRequest(
        silver_id=silver_id,
        use_case=UseCase(use_case),
        data_shape=DataShape(data_shape),
        target_model=TargetModel(target_model),
        objective=Objective(objective),
        adapter_name=adapter_name,
        pii_mask=pii_mask.lower() == "true",
        options={k: str(v) for k, v in opts.items()},
    )
    service = create_pipeline_service()
    result = service.materialize_from_text(silver_cdm_text, request)
    return json.dumps(result.model_dump())
