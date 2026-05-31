# FormaForge — AI Assistant Context

This file provides codebase context for AI assistants (Claude Code, etc.) working on this repository.

---

## Module Map

```
src/formaforge/
├── ai/               AiConverter (sync + async Anthropic API calls), prompt templates
├── bronze/           BronzeIngester: raw file ingestion, MIME detection, checksum
├── export/           BronzePacker: ZIP export with manifest + mechanical AI restore guide
├── gold/
│   ├── adapters/     BaseAdapter + 8 built-in adapters, AdapterRegistry singleton
│   ├── materializer.py   GoldMaterializer: CDM → Gold via adapter + token counting
│   ├── policy.py         PolicyEngine: (UseCase, DataShape, Objective) → adapter name
│   └── token_counter.py  TokenCounter: model-specific token estimation
├── mcp/
│   ├── server.py     FastMCP server wiring all tools
│   └── tools/        8 MCP tool functions (one file each)
├── models/           Pydantic models: BronzeRecord, CdmDocument, GoldRequest/Result
├── silver/
│   ├── cdm_migrator.py   CdmMigrator: v1.0→v2.0 schema migration
│   ├── cdm_parser.py     CdmParser: CDM Markdown text → CdmDocument
│   ├── cdm_writer.py     CdmWriter: CdmDocument → CDM Markdown text
│   ├── converters/       Deterministic format converters (one file per format)
│   ├── normalizer.py     SilverNormalizer: routes BronzeRecord to correct converter
│   └── pii_detector.py   PiiDetector: presidio wrapper with graceful degradation
└── storage/          Alembic migrations (SQLAlchemy, not yet used by main pipeline)
```

---

## Data Flow

```
ingest_to_bronze(content_b64, source_uri, filename)
    → BronzeIngester.ingest()
    → BronzeRecord {id, source_uri, source_format, structure_class, raw_content_path}

normalize_to_silver(bronze_id, conversion_method="auto")
    → SilverNormalizer.normalize(record, ConversionMethod.AUTO)
    → CdmDocument {frontmatter: CdmFrontmatter, title, body, blocks}

materialize_gold(cdm_text, adapter_name, pii_mask, options)
    → GoldMaterializer.materialize(GoldRequest)
    → GoldResult {silver_id, adapter_name, text, byte_count, token_estimate}
```

---

## Key Models

### `BronzeRecord` — `src/formaforge/models/bronze.py`

```python
id: str                  # UUID
source_uri: str          # original location (s3://, file://, etc.)
source_format: str       # "json", "pdf", "txt", etc.
structure_class: StructureClass  # STRUCTURED | UNSTRUCTURED
raw_content_path: str    # absolute path to stored raw bytes
ingested_at: datetime
checksum: str            # SHA-256 hex
```

### `CdmDocument` / `CdmFrontmatter` — `src/formaforge/models/silver.py`

```python
# CdmFrontmatter
source_format: str
source_uri: str
structure_class: str
normalized_at: datetime
conversion_method: ConversionMethod   # "deterministic" | "ai" | "auto"
conversion_confidence: float          # 0.0–1.0
cdm_schema_version: str               # "2.0" (current)
pii_flags: list[str]                  # detected PII entity types

# CdmDocument
frontmatter: CdmFrontmatter
title: str
body: str
blocks: list[CdmTableBlock | CdmDataBlock]
```

### `GoldRequest` / `GoldResult` — `src/formaforge/models/gold.py`

```python
# GoldRequest
silver_id: str
use_case: UseCase          # prompt_context | rag_kb | tool_schema | finetune
target_model: TargetModel  # claude | gpt4 | gemini | small | frontier | generic
data_shape: DataShape      # nested | flat_table | uniform_array | irregular | document | conversation
objective: Objective       # accuracy | cost | balance
adapter_name: str | None   # override policy if set
pii_mask: bool

# GoldResult
silver_id: str
adapter_name: str
text: str
byte_count: int
token_estimate: int
```

---

## Silver Conversion Routing

`SilverNormalizer._resolve_method()` logic (in `src/formaforge/silver/normalizer.py`):

1. If `conversion_method != AUTO` → use it directly
2. If `structure_class == STRUCTURED` → `DETERMINISTIC`
3. If format in `{"pdf", "docx", "xlsx"}` → `DETERMINISTIC`
4. Otherwise → `AI`

`_DETERMINISTIC_CONVERTERS` dict maps format strings to converter instances. Adding a new format: inherit `BaseConverter`, implement `convert_bytes(raw: bytes, source_uri: str) -> CdmDocument`, add to the dict.

---

## Gold Adapter Extension

Built-in adapters live in `src/formaforge/gold/adapters/`. The registry is a singleton:

```python
AdapterRegistry.instance().register("my_adapter", MyAdapter())
```

`_BUILTIN_ADAPTERS` in `src/formaforge/gold/adapters/__init__.py` seeds the registry at import time.

To add a new built-in adapter:
1. `src/formaforge/gold/adapters/my_adapter.py` — inherit `BaseAdapter`, implement `render(doc: CdmDocument) -> str`
2. Add to `_BUILTIN_ADAPTERS` in `__init__.py`
3. Add a policy rule in `src/formaforge/gold/policy.py`

---

## AI Conversion

`src/formaforge/ai/ai_converter.py`:

- `AiConverter.convert(raw, source_uri, source_format) -> CdmDocument` — synchronous
- `AiConverter.convert_async(raw, source_uri, source_format) -> CdmDocument` — async, uses `AsyncAnthropic` + `messages.stream()`, accumulates `text_stream` chunks before parsing
- Both fall back to `_fallback_doc()` (low-confidence stub) if parsing fails
- `_async_client` is created once in `__init__`, not per call

`CdmMigrator.migrate_text(text, source_uri="")` in `src/formaforge/silver/cdm_migrator.py`:
- Text starts with `---` → parse as v2.0 (or v1.0 frontmatter) then migrate
- Text does not start with `---` → treat as v1.0 legacy (no frontmatter), extract H1 title, migrate to v2.0

---

## PII Detection

`src/formaforge/silver/pii_detector.py`:

- `PiiDetector().detect(text) -> list[str]` — returns deduplicated entity type list (`["PERSON", "EMAIL_ADDRESS"]`)
- `PiiDetector().mask(text) -> str` — replaces PII with `<ENTITY_TYPE>` placeholders
- `FORMAFORGE_SKIP_PII=1` env var → returns `[]` / identity immediately (no presidio call)
- presidio not installed → silently returns `[]` / identity (graceful degradation)
- presidio is an optional dep: `uv sync --extra pii`

---

## Test Conventions

- `tests/unit/` — pure unit tests, mock all external I/O and API calls
- `tests/integration/` — real file I/O via `tmp_path`, no network calls
- Async tests: `@pytest.mark.asyncio` (mode=AUTO in `pyproject.toml`, no explicit decorator needed in most cases)
- Mocking async streaming:

```python
def _make_stream_mock(full_text: str) -> MagicMock:
    chunks = [full_text[i:i+20] for i in range(0, len(full_text), 20)]
    async def _aiter():
        for chunk in chunks:
            yield chunk
    stream_mock = MagicMock()
    stream_mock.__aenter__ = AsyncMock(return_value=stream_mock)
    stream_mock.__aexit__ = AsyncMock(return_value=False)
    stream_mock.text_stream = _aiter()
    return stream_mock
```

- Patching `AiConverter` in normalizer tests: `patch("formaforge.silver.normalizer.AiConverter")`
  - `AiConverter` must be imported at module level in `normalizer.py` for this to work
- Patching `AsyncAnthropic`: `patch("formaforge.ai.ai_converter.anthropic.AsyncAnthropic", return_value=mock_async_client)`

---

## Environment Variables

| Variable | Used by | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | `AiConverter.__init__` | Required for AI path; `require_api_key=False` by default (won't raise without it) |
| `FORMAFORGE_SKIP_PII` | `PiiDetector` | Set to `1` in CI to skip presidio |

---

## Key Constraints

- **`CdmParser.parse()` requires frontmatter** — raises `ValueError("CDM document missing YAML frontmatter")` if the text doesn't start with `---`. For legacy documents, use `CdmMigrator.migrate_text()` instead.
- **Module-level imports required for patching** — if `AiConverter` is imported inside a function body, `patch("formaforge.silver.normalizer.AiConverter")` won't find it. Keep imports at module level.
- **`AdapterRegistry` is a singleton** — `AdapterRegistry.instance()` always returns the same object; tests that register adapters may affect other tests if not isolated.
- **TokenCounter model dispatch** — `gpt4` uses tiktoken (optional dep); `gemini` uses byte/3; all others use byte/4. Install with `uv sync --extra tokens`.
- **Binary converters** (PDF/DOCX/XLSX) are optional deps — install with `uv sync --extra binary`. The converter classes exist but will raise `ImportError` at call time if the underlying library is missing.

---

## CI / Pre-commit

Pre-commit hooks (`.pre-commit-config.yaml`): `ruff`, `ruff-format`, trailing whitespace, end-of-file, yaml/toml check, large files, merge conflicts, `mypy`.

GitHub Actions (`.github/workflows/`): runs on push/PR to `main`, executes `uv run pytest` + `uv run ruff check` + `uv run mypy src/`. Coverage threshold ≥ 80%.

Local equivalent: `make check` (see root `Makefile`; `make help` for all targets).
