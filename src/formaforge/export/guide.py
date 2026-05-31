"""Mechanically generate AI-oriented restore documentation from manifest data."""

from __future__ import annotations

from formaforge.export.manifest import ArchiveManifest


class GuideGenerator:
    def render(self, manifest: ArchiveManifest) -> str:
        tree = "\n".join(f"- {line}" for line in manifest.file_tree_lines())
        table_rows = "\n".join(
            "| {bronze_id} | {source_uri} | {source_format} | {structure_class} | "
            "`{checksum}` | `{archive_path}` |".format(
                bronze_id=e.bronze_id,
                source_uri=e.source_uri.replace("|", "\\|"),
                source_format=e.source_format,
                structure_class=e.structure_class,
                checksum=e.checksum,
                archive_path=e.archive_path,
            )
            for e in sorted(manifest.records, key=lambda r: r.bronze_id)
        )
        normalize_examples = "\n".join(
            f'  - `normalize_to_silver(bronze_id="{e.bronze_id}")`'
            for e in sorted(manifest.records, key=lambda r: r.bronze_id)
        )
        checksum_steps = "\n".join(
            f"  - `{e.archive_path}`: expected SHA-256 `{e.raw_sha256}` ({e.raw_byte_count} bytes)"
            for e in sorted(manifest.records, key=lambda r: r.bronze_id)
        )

        return f"""# FormaForge Bronze Archive — AI Restore Guide

> This file is generated mechanically from `manifest.json`. Do not edit by hand;
> regenerate the archive with `formaforge pack` if metadata changes.

## Archive identity

| Field | Value |
|-------|-------|
| archive_format_version | `{manifest.archive_format_version}` |
| formaforge_version | `{manifest.formaforge_version}` |
| packed_at | `{manifest.packed_at.isoformat()}` |
| source_storage_dir | `{manifest.source_storage_dir}` |
| record_count | {manifest.record_count} |

## ZIP layout

{tree}

## Records

| bronze_id | source_uri | source_format | structure_class | checksum | archive_path |
|-----------|------------|-----------------|-----------------|----------|----------------|
{table_rows}

## Restore in another environment

1. Extract this ZIP to a working directory (e.g. `unzip formaforge-bronze.zip -d ./restore`).
2. Copy the `bronze/` directory into the target FormaForge Bronze storage path:
   - `export FORMAFORGE_STORAGE_DIR=/path/to/bronze`
   - `cp -R bronze/* "$FORMAFORGE_STORAGE_DIR"/`
3. Verify each `raw` file against the manifest checksums (SHA-256):
{checksum_steps}
4. Start FormaForge (`formaforge serve`) or use MCP tools against the restored storage.
5. For each Bronze record, run Silver normalization (examples for this archive):
{normalize_examples}
6. After obtaining CDM text from step 5, call `recommend_format` then `materialize_gold` as needed.

## Notes for automated agents

- Treat `bronze/{{id}}/meta.json` as authoritative metadata; do not rewrite checksums.
- Treat `bronze/{{id}}/raw` as opaque bytes; preserve encoding and line endings.
- Read `manifest.json` for machine-parseable fields identical to this guide.
- An empty Bronze storage directory cannot be packed; ingest data first with `ingest_to_bronze`.
"""
