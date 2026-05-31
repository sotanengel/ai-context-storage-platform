"""MCP tool: list_formats."""

import json

from formaforge.services.pipeline import create_pipeline_service


def list_formats() -> str:
    """List all registered Gold format adapters.

    Returns:
        JSON array with adapter name and class for each registered adapter.
    """
    service = create_pipeline_service()
    return json.dumps(service.list_adapters())
