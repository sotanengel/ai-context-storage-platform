"""FormaForge CLI entry point."""

import typer

app = typer.Typer(help="FormaForge: multi-format to AI-optimal conversion platform.")


@app.command()
def serve(
    transport: str = typer.Option(
        "stdio",
        help="Transport protocol: stdio | sse | streamable-http",
    ),
    host: str = typer.Option("127.0.0.1", help="Bind host (for sse/streamable-http)"),
    port: int = typer.Option(8000, help="Bind port (for sse/streamable-http)"),
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


if __name__ == "__main__":
    app()
