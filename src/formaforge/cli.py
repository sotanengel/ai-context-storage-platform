"""FormaForge CLI entry point."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import typer

app = typer.Typer(help="FormaForge: multi-format to AI-optimal conversion platform.")


@app.command()
def serve(
    transport: str = typer.Option(
        "stdio",
        help="Transport protocol: stdio | sse | streamable-http",
        envvar="FORMAFORGE_TRANSPORT",
    ),
    host: str = typer.Option(
        "127.0.0.1",
        help="Bind host (for sse/streamable-http)",
        envvar="FORMAFORGE_HOST",
    ),
    port: int = typer.Option(
        8000,
        help="Bind port (for sse/streamable-http)",
        envvar="FORMAFORGE_PORT",
    ),
) -> None:
    """Start the MCP server."""
    from formaforge.mcp.server import create_server

    valid: tuple[str, ...] = ("stdio", "sse", "streamable-http")
    if transport not in valid:
        raise typer.BadParameter(f"transport must be one of {valid}")
    create_server(host=host, port=port).run(
        transport=transport  # type: ignore[arg-type]
    )


@app.command()
def version() -> None:
    """Show the current version."""
    from formaforge import __version__

    typer.echo(f"formaforge {__version__}")


@app.command("pack")
def pack(
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output .zip path (default: formaforge-bronze-<UTC>.zip)"
    ),
    storage_dir: str | None = typer.Option(
        None,
        "--storage-dir",
        help="Bronze storage directory",
        envvar="FORMAFORGE_STORAGE_DIR",
    ),
) -> None:
    """Pack ingested Bronze data into a ZIP with an AI restore guide."""
    from formaforge.config import resolve_storage_dir
    from formaforge.export.packer import BronzePacker, EmptyBronzeStorageError
    from formaforge.export.scanner import BronzeStorageScanner, InvalidBronzeStorageError

    resolved_storage = resolve_storage_dir(Path(storage_dir) if storage_dir else None)
    output_path = (
        Path(output)
        if output is not None
        else Path(f"formaforge-bronze-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.zip")
    )

    try:
        manifest = BronzeStorageScanner().scan(resolved_storage)
        result = BronzePacker().pack(manifest, resolved_storage, output_path)
    except EmptyBronzeStorageError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except InvalidBronzeStorageError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"Packed {manifest.record_count} record(s) to {result}")


if __name__ == "__main__":
    app()
