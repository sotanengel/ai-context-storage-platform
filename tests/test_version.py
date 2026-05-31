"""Smoke test: verify the package installs and exposes the correct version."""

import formaforge


def test_version_exists() -> None:
    assert hasattr(formaforge, "__version__")


def test_version_is_string() -> None:
    assert isinstance(formaforge.__version__, str)


def test_version_value() -> None:
    assert formaforge.__version__ == "0.1.0"
