"""Pytest configuration and shared fixtures."""

import pytest

from formaforge.gold.adapters import AdapterRegistry


@pytest.fixture(autouse=True)
def _reset_adapter_registry() -> None:
    yield
    AdapterRegistry.reset_for_testing()
