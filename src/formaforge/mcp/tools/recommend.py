"""MCP tool: recommend_format."""

import json

from formaforge.models.gold import DataShape, Objective, TargetModel, UseCase
from formaforge.services.pipeline import create_pipeline_service


def recommend_format(
    use_case: str,
    data_shape: str,
    target_model: str = "generic",
    objective: str = "balance",
) -> str:
    """Recommend the optimal Gold format for the given parameters.

    Returns:
        JSON string with format, rationale, and estimated savings.
    """
    service = create_pipeline_service()
    result = service.recommend(
        use_case=UseCase(use_case),
        data_shape=DataShape(data_shape),
        target_model=TargetModel(target_model),
        objective=Objective(objective),
    )
    return json.dumps(result)
