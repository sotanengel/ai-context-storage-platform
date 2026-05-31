"""Tests for the Gold policy engine."""

from formaforge.gold.policy import PolicyEngine
from formaforge.models.gold import DataShape, Objective, TargetModel, UseCase


def test_prompt_context_nested_accuracy_returns_yaml() -> None:
    engine = PolicyEngine()
    result = engine.recommend(
        use_case=UseCase.PROMPT_CONTEXT,
        data_shape=DataShape.NESTED,
        target_model=TargetModel.GENERIC,
        objective=Objective.ACCURACY,
    )
    assert result == "yaml"


def test_prompt_context_flat_table_accuracy_returns_markdown_kv() -> None:
    engine = PolicyEngine()
    result = engine.recommend(
        use_case=UseCase.PROMPT_CONTEXT,
        data_shape=DataShape.FLAT_TABLE,
        target_model=TargetModel.GENERIC,
        objective=Objective.ACCURACY,
    )
    assert result == "markdown_kv"


def test_prompt_context_flat_table_cost_returns_csv() -> None:
    engine = PolicyEngine()
    result = engine.recommend(
        use_case=UseCase.PROMPT_CONTEXT,
        data_shape=DataShape.FLAT_TABLE,
        target_model=TargetModel.GENERIC,
        objective=Objective.COST,
    )
    assert result == "csv"


def test_rag_kb_document_balance_returns_markdown() -> None:
    engine = PolicyEngine()
    result = engine.recommend(
        use_case=UseCase.RAG_KB,
        data_shape=DataShape.DOCUMENT,
        target_model=TargetModel.CLAUDE,
        objective=Objective.BALANCE,
    )
    assert result == "markdown_kv"


def test_finetune_conversation_returns_jsonl() -> None:
    engine = PolicyEngine()
    result = engine.recommend(
        use_case=UseCase.FINETUNE,
        data_shape=DataShape.CONVERSATION,
        target_model=TargetModel.GPT4,
        objective=Objective.BALANCE,
    )
    assert result == "jsonl"


def test_unmatched_falls_back_to_yaml() -> None:
    engine = PolicyEngine()
    result = engine.recommend(
        use_case=UseCase.TOOL_SCHEMA,
        data_shape=DataShape.IRREGULAR,
        target_model=TargetModel.GENERIC,
        objective=Objective.BALANCE,
    )
    assert result in ("yaml", "json")
