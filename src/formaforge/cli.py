"""FormaForge CLI entry point."""

import typer

app = typer.Typer(help="FormaForge: multi-format to AI-optimal conversion platform.")


@app.command()
def serve() -> None:
    """Start the MCP server (stdio transport)."""
    from formaforge.mcp.server import create_server

    create_server().run()


@app.command()
def version() -> None:
    """Show the current version."""
    from formaforge import __version__

    typer.echo(f"formaforge {__version__}")


if __name__ == "__main__":
    app()
