"""FormaForge MCP server."""

from mcp.server.fastmcp import FastMCP

from formaforge.mcp.tools.benchmark import benchmark_format
from formaforge.mcp.tools.compare import compare_formats
from formaforge.mcp.tools.ingest import ingest_to_bronze
from formaforge.mcp.tools.list_formats import list_formats
from formaforge.mcp.tools.materialize import materialize_gold
from formaforge.mcp.tools.normalize import normalize_to_silver
from formaforge.mcp.tools.recommend import recommend_format
from formaforge.mcp.tools.register_adapter import register_format_adapter


def create_server(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    server = FastMCP("formaforge", host=host, port=port)

    server.add_tool(ingest_to_bronze)
    server.add_tool(normalize_to_silver)
    server.add_tool(recommend_format)
    server.add_tool(materialize_gold)
    server.add_tool(compare_formats)
    server.add_tool(list_formats)
    server.add_tool(register_format_adapter)
    server.add_tool(benchmark_format)

    return server


if __name__ == "__main__":
    create_server().run()
