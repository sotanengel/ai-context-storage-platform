"""Policy engine: select the optimal Gold adapter based on use-case parameters."""

from formaforge.models.gold import DataShape, Objective, TargetModel, UseCase

_POLICY_TABLE: list[tuple[tuple[UseCase, DataShape, Objective], str]] = [
    ((UseCase.PROMPT_CONTEXT, DataShape.NESTED, Objective.ACCURACY), "yaml"),
    ((UseCase.PROMPT_CONTEXT, DataShape.NESTED, Objective.COST), "toon"),
    ((UseCase.PROMPT_CONTEXT, DataShape.FLAT_TABLE, Objective.ACCURACY), "markdown_kv"),
    ((UseCase.PROMPT_CONTEXT, DataShape.FLAT_TABLE, Objective.COST), "csv"),
    ((UseCase.PROMPT_CONTEXT, DataShape.UNIFORM_ARRAY, Objective.COST), "csv"),
    ((UseCase.RAG_KB, DataShape.DOCUMENT, Objective.BALANCE), "markdown_kv"),
    ((UseCase.FINETUNE, DataShape.CONVERSATION, Objective.BALANCE), "jsonl"),
]

_DEFAULT_ADAPTER = "yaml"


class PolicyEngine:
    def recommend(
        self,
        use_case: UseCase,
        data_shape: DataShape,
        target_model: TargetModel,
        objective: Objective,
    ) -> str:
        for (uc, ds, obj), adapter in _POLICY_TABLE:
            if use_case == uc and data_shape == ds and objective == obj:
                return adapter
        if use_case == UseCase.FINETUNE:
            return "jsonl"
        if use_case == UseCase.TOOL_SCHEMA:
            return "json"
        return _DEFAULT_ADAPTER
