"""MCP tool: list_formats."""

import json

from formaforge.gold.materializer import GoldMaterializer


def list_formats() -> str:
    """List all registered Gold format adapters.

    Returns:
        JSON array with adapter name and class for each registered adapter.
    """
    return json.dumps(GoldMaterializer().list_adapters())
