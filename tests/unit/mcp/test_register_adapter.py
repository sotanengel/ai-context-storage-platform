"""Tests for register_format_adapter MCP tool."""

import json
import sys
import types

from formaforge.mcp.tools.register_adapter import register_format_adapter


def _make_module(name: str, class_name: str, base: type) -> None:
    """Inject a synthetic module into sys.modules."""
    mod = types.ModuleType(name)
    cls = type(
        class_name,
        (base,),
        {"adapter_name": class_name.lower(), "render": lambda self, doc, **opts: ""},
    )
    setattr(mod, class_name, cls)
    sys.modules[name] = mod


def test_register_valid_adapter() -> None:
    from formaforge.gold.adapters.base import BaseAdapter

    _make_module("mytest.adapters.custom", "CustomAdapter", BaseAdapter)
    result = register_format_adapter(
        name="custom_test",
        module_path="mytest.adapters.custom",
        class_name="CustomAdapter",
    )
    parsed = json.loads(result)
    assert parsed["adapter_id"] == "custom_test"
    assert parsed["status"] == "registered"


def test_register_nonexistent_module() -> None:
    result = register_format_adapter(
        name="bad_module",
        module_path="nonexistent.module.xyz",
        class_name="SomeClass",
    )
    parsed = json.loads(result)
    assert "error" in parsed


def test_register_not_a_base_adapter() -> None:
    mod = types.ModuleType("mytest.not_adapter")
    mod.NotAdapter = type("NotAdapter", (object,), {})  # type: ignore[attr-defined]
    sys.modules["mytest.not_adapter"] = mod
    result = register_format_adapter(
        name="not_adapter",
        module_path="mytest.not_adapter",
        class_name="NotAdapter",
    )
    parsed = json.loads(result)
    assert "error" in parsed


def test_register_missing_class() -> None:
    mod = types.ModuleType("mytest.empty_mod")
    sys.modules["mytest.empty_mod"] = mod
    result = register_format_adapter(
        name="missing_cls",
        module_path="mytest.empty_mod",
        class_name="DoesNotExist",
    )
    parsed = json.loads(result)
    assert "error" in parsed


def test_registered_adapter_in_registry() -> None:
    from formaforge.gold.adapters import AdapterRegistry
    from formaforge.gold.adapters.base import BaseAdapter

    _make_module("mytest.adapters.reg_check", "RegCheckAdapter", BaseAdapter)
    register_format_adapter(
        name="reg_check",
        module_path="mytest.adapters.reg_check",
        class_name="RegCheckAdapter",
    )
    registry = AdapterRegistry.instance()
    assert registry.get("reg_check") is not None
