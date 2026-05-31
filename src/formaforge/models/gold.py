"""Gold layer data models."""

from enum import StrEnum

from pydantic import BaseModel, Field


class UseCase(StrEnum):
    PROMPT_CONTEXT = "prompt_context"
    RAG_KB = "rag_kb"
    TOOL_SCHEMA = "tool_schema"
    FINETUNE = "finetune"


class TargetModel(StrEnum):
    CLAUDE = "claude"
    GPT4 = "gpt4"
    GEMINI = "gemini"
    SMALL = "small"
    FRONTIER = "frontier"
    GENERIC = "generic"


class DataShape(StrEnum):
    NESTED = "nested"
    FLAT_TABLE = "flat_table"
    UNIFORM_ARRAY = "uniform_array"
    IRREGULAR = "irregular"
    DOCUMENT = "document"
    CONVERSATION = "conversation"


class Objective(StrEnum):
    ACCURACY = "accuracy"
    COST = "cost"
    BALANCE = "balance"


class GoldRequest(BaseModel):
    silver_id: str
    use_case: UseCase = UseCase.PROMPT_CONTEXT
    target_model: TargetModel = TargetModel.GENERIC
    data_shape: DataShape = DataShape.DOCUMENT
    objective: Objective = Objective.BALANCE
    adapter_name: str | None = None
    options: dict[str, str] = Field(default_factory=dict)


class GoldResult(BaseModel):
    silver_id: str
    adapter_name: str
    text: str
    byte_count: int
    token_estimate: int
    options: dict[str, str] = Field(default_factory=dict)


class BenchmarkResult(BaseModel):
    adapter: str
    latency_ms: float
    byte_count: int
    token_estimate: int
    fidelity_score: float = Field(ge=0.0, le=1.0)
    error: str | None = None
