"""MCP tool: register_format_adapter."""

import importlib
import json

from formaforge.gold.adapters.base import BaseAdapter
from formaforge.services.pipeline import create_pipeline_service


def register_format_adapter(
    name: str,
    module_path: str,
    class_name: str,
) -> str:
    """Dynamically register a new Gold format adapter.

    Args:
        name: Unique adapter name.
        module_path: Python module path, e.g. 'mypackage.adapters.custom'.
        class_name: Class name within the module.

    Returns:
        JSON with adapter_id on success, or error message.
    """
    try:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        if not (isinstance(cls, type) and issubclass(cls, BaseAdapter)):
            return json.dumps({"error": f"{class_name} is not a BaseAdapter subclass."})
        instance = cls()
        service = create_pipeline_service()
        service.register_adapter(name, instance)
        return json.dumps({"adapter_id": name, "status": "registered"})
    except (ImportError, AttributeError) as exc:
        return json.dumps({"error": str(exc)})
