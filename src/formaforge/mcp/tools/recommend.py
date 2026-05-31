"""MCP tool: recommend_format."""

import json

from formaforge.gold.policy import PolicyEngine
from formaforge.models.gold import DataShape, Objective, TargetModel, UseCase


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
    engine = PolicyEngine()
    adapter = engine.recommend(
        use_case=UseCase(use_case),
        data_shape=DataShape(data_shape),
        target_model=TargetModel(target_model),
        objective=Objective(objective),
    )
    rationale = _rationale(use_case, data_shape, objective, adapter)
    return json.dumps({"format": adapter, "rationale": rationale})


def _rationale(use_case: str, data_shape: str, objective: str, adapter: str) -> str:
    return (
        f"For use_case={use_case!r}, data_shape={data_shape!r}, "
        f"objective={objective!r}: {adapter!r} selected per research-backed policy."
    )
