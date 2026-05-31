# FormaForge

**Multi-format → AI-optimal format conversion platform / 多形式データを生成AI最適形式へ変換するプラットフォーム**

異種フォーマットで蓄積されたデータを単一の正規化テキスト表現（Silver）に統一し、用途・モデル・構造・目的に応じて生成AIに最適なデータ形式（Gold）へ動的に出力する。その機能を MCP ツールとして生成 AI 自身が直接呼び出せる。

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Raw Input (any format)                                     │
│  JSON / YAML / CSV / XML / TOML / Markdown / PDF / DOCX /  │
│  XLSX / plain text / …                                      │
└────────────────────────┬────────────────────────────────────┘
                         │ ingest_to_bronze
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Bronze Layer  (src/formaforge/bronze/)                     │
│  Raw bytes stored on disk with metadata (BronzeRecord)      │
│  MIME detection, checksum, source_uri tracking              │
└────────────────────────┬────────────────────────────────────┘
                         │ normalize_to_silver
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Silver Layer  (src/formaforge/silver/)                     │
│  Canonical Document Model (CDM) — YAML frontmatter +        │
│  Markdown body (CdmDocument)                                │
│  Structured formats → deterministic converters              │
│  Unstructured text → AI-assisted conversion (Anthropic)     │
└────────────────────────┬────────────────────────────────────┘
                         │ materialize_gold
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Gold Layer  (src/formaforge/gold/)                         │
│  Adapter-rendered output optimised for target use case:     │
│  json / yaml / jsonl / csv / xml / plaintext / toon /       │
│  markdown_kv                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Anthropic API key (required for AI-assisted Silver conversion of unstructured text)

### Install

```bash
git clone https://github.com/sotanengel/ai-context-storage-platform.git
cd ai-context-storage-platform
uv sync --all-extras
```

### Environment setup

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

### Start the MCP server

```bash
# stdio transport (default — use with Claude Desktop / Claude Code)
formaforge serve

# SSE transport (HTTP streaming)
formaforge serve --transport sse --host 127.0.0.1 --port 8000

# Streamable HTTP transport
formaforge serve --transport streamable-http --port 8000
```

### Docker

Prerequisites: Docker Engine and Docker Compose v2.

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

docker compose up --build
```

The container listens on `http://localhost:8000` with `streamable-http` transport by default.
Bronze data is persisted in the `formaforge-data` Docker volume (`FORMAFORGE_STORAGE_DIR=/data/bronze`).

Useful commands:

```bash
make docker-build   # build image only
make docker-up      # build and start in foreground
make docker-down    # stop containers
```

For stdio transport (e.g. Claude Desktop via `docker run -i`):

```bash
docker compose run --rm -i formaforge formaforge serve --transport stdio
```

---

## CLI Reference

| Command | Description |
|---|---|
| `formaforge serve` | Start the MCP server |
| `formaforge serve --transport sse --host HOST --port PORT` | Start with HTTP transport |
| `formaforge pack` | Pack Bronze storage into a ZIP with manifest and AI restore guide |
| `formaforge version` | Print version and exit |

**`formaforge pack` options**

| Option | Default | Description |
|---|---|---|
| `--output` / `-o` | `formaforge-bronze-<UTC timestamp>.zip` | Output ZIP path |
| `--storage-dir` | `FORMAFORGE_STORAGE_DIR` or `~/.formaforge/bronze` | Bronze storage directory to pack |

The ZIP includes `manifest.json`, `FORMAFORGE_AI_RESTORE_GUIDE.md` (mechanically generated from the manifest), and a `bronze/` tree mirroring the storage layout.

**`formaforge serve` options**

| Option | Default | Values |
|---|---|---|
| `--transport` | `stdio` | `stdio`, `sse`, `streamable-http` |
| `--host` | `127.0.0.1` | Any valid hostname/IP |
| `--port` | `8000` | Any valid port number |

---

## MCP Tools Reference

All tools are available via the MCP server. AI assistants can call them directly.

### `ingest_to_bronze`

Ingest raw content (base64-encoded) and store as a Bronze record.

| Parameter | Type | Description |
|---|---|---|
| `content_b64` | `str` | Base64-encoded file content |
| `source_uri` | `str` | Original URI (e.g. `s3://bucket/file.pdf`) |
| `filename` | `str` | Filename with extension for format detection |

Returns: serialized `BronzeRecord` JSON.

### `normalize_to_silver`

Convert a Bronze record to a CDM (Silver) document.

| Parameter | Type | Description |
|---|---|---|
| `bronze_id` | `str` | ID from `ingest_to_bronze` |
| `conversion_method` | `str` | `"auto"` (default), `"ai"`, or `"deterministic"` |

Returns: CDM Markdown text with YAML frontmatter.

### `recommend_format`

Recommend the optimal Gold adapter for a given use case.

| Parameter | Type | Description |
|---|---|---|
| `cdm_text` | `str` | CDM Markdown from `normalize_to_silver` |
| `use_case` | `str` | `"prompt_context"`, `"rag_kb"`, `"tool_schema"`, `"finetune"` |
| `target_model` | `str` | `"claude"`, `"gpt4"`, `"gemini"`, `"small"`, `"frontier"`, `"generic"` |
| `objective` | `str` | `"accuracy"`, `"cost"`, `"balance"` |

Returns: recommended adapter name and rationale.

### `materialize_gold`

Render a CDM document to a Gold format.

| Parameter | Type | Description |
|---|---|---|
| `cdm_text` | `str` | CDM Markdown from `normalize_to_silver` |
| `adapter_name` | `str` | Name of the Gold adapter to use |
| `pii_mask` | `bool` | Mask PII entities in output (default: `false`) |
| `options` | `dict` | Adapter-specific options (optional) |

Returns: `GoldResult` with rendered text, byte count, and token estimate.

### `compare_formats`

Compare multiple adapters on the same CDM document side by side.

| Parameter | Type | Description |
|---|---|---|
| `cdm_text` | `str` | CDM Markdown |
| `adapter_names` | `list[str]` | Adapters to compare |

Returns: table of byte counts and token estimates per adapter.

### `benchmark_format`

Benchmark a single adapter with latency and fidelity scoring.

| Parameter | Type | Description |
|---|---|---|
| `cdm_text` | `str` | CDM Markdown |
| `adapter_name` | `str` | Adapter to benchmark |

Returns: `BenchmarkResult` with latency, byte count, token estimate, fidelity score.

### `list_formats`

List all registered Gold adapters with metadata.

### `register_format_adapter`

Dynamically register a custom `BaseAdapter` subclass at runtime.

| Parameter | Type | Description |
|---|---|---|
| `module_path` | `str` | Python import path (e.g. `mypackage.adapters.MyAdapter`) |
| `adapter_name` | `str` | Name to register under |

---

## Gold Adapters

| Adapter | Format | Best for |
|---|---|---|
| `json` | JSON | Tool schemas, structured APIs |
| `yaml` | YAML | Human-readable configs, RAG KB |
| `jsonl` | JSON Lines | Fine-tuning datasets |
| `csv` | CSV | Tabular data, spreadsheet import |
| `xml` | XML | Legacy system integration |
| `plaintext` | Plain text | Simple prompt context |
| `toon` | TOON (compact brace notation) | Token-efficient nested data |
| `markdown_kv` | Markdown key-value | Readable prompt context |

**TOON (Token-Optimized Object Notation)** uses `{key:value key2:value2}` brace syntax instead of JSON,
reducing token count by ~5% for nested objects.

---

## Silver Conversion Routing

`SilverNormalizer` automatically selects a conversion strategy based on file format and structure:

| Condition | Strategy |
|---|---|
| `structure_class = structured` | Deterministic converter |
| Format is `pdf`, `docx`, or `xlsx` | Deterministic converter (binary parser) |
| Format is `json`, `yaml`, `csv`, `xml`, `toml`, `markdown` | Deterministic converter |
| Everything else (plain text, etc.) | AI-assisted via Anthropic API |

Force a specific strategy with `conversion_method="ai"` or `conversion_method="deterministic"`.

---

## CDM Schema Versioning

The Canonical Document Model uses YAML frontmatter with `cdm_schema_version`:

- **v2.0** (current): full YAML frontmatter block required
- **v1.0** (legacy): plain Markdown without frontmatter

Use `CdmMigrator.migrate_text(text)` to parse any version and upgrade to v2.0 automatically.

---

## Development Guide

ローカル開発コマンドは `make` で短縮できます。一覧は `make help` で確認できます。

### Setup

```bash
make setup    # 依存関係インストール + pre-commit フック設定
make sync     # 依存関係のみ再同期
```

### Run tests

```bash
make test           # 全テスト（カバレッジ付き）
make test-unit      # ユニットテストのみ（高速）
uv run pytest -k "test_normalizer"   # 名前でフィルタ（直接実行）
```

### Lint and type check

```bash
make lint       # ruff lint（CI と一致）
make fmt        # フォーマット適用
make fmt-check  # フォーマットチェック（CI と一致）
make type       # mypy 型チェック（CI と一致）
make check      # CI 相当の一括検証（PR 前に推奨）
make hooks      # pre-commit 全フック実行
```

### Adding a new Gold adapter

1. Create `src/formaforge/gold/adapters/my_adapter.py` inheriting `BaseAdapter` and implementing `render(doc) -> str`
2. Register in `src/formaforge/gold/adapters/__init__.py` under `_BUILTIN_ADAPTERS`
3. Add a policy rule in `src/formaforge/gold/policy.py` mapping `(UseCase, DataShape, Objective) → "my_adapter"`

### Adding a new Silver converter (deterministic)

1. Create `src/formaforge/silver/converters/my_converter.py` inheriting `BaseConverter` and implementing `convert_bytes(raw, source_uri) -> CdmDocument`
2. Add the format key to `_DETERMINISTIC_CONVERTERS` in `src/formaforge/silver/normalizer.py`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (for AI path) | Anthropic API key for unstructured text conversion |
| `FORMAFORGE_SKIP_PII` | No | Set to `1` to skip PII detection (useful in CI) |
| `FORMAFORGE_STORAGE_DIR` | No | Bronze storage directory (default: `~/.formaforge/bronze`; Docker: `/data/bronze`) |
| `FORMAFORGE_TRANSPORT` | No | MCP transport for `formaforge serve` (default: `stdio`; Docker: `streamable-http`) |
| `FORMAFORGE_HOST` | No | Bind host for HTTP transports (default: `127.0.0.1`; Docker: `0.0.0.0`) |
| `FORMAFORGE_PORT` | No | Bind port for HTTP transports (default: `8000`) |

---

## License

See [LICENSE](LICENSE).
