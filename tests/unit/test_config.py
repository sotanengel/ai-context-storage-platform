"""Tests for formaforge.config."""

from pathlib import Path

import pytest

from formaforge.config import resolve_storage_dir


def test_resolve_storage_dir_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FORMAFORGE_STORAGE_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert resolve_storage_dir() == tmp_path / ".formaforge" / "bronze"


def test_resolve_storage_dir_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FORMAFORGE_STORAGE_DIR", "/data/bronze")
    assert resolve_storage_dir() == Path("/data/bronze")


def test_resolve_storage_dir_override_takes_precedence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FORMAFORGE_STORAGE_DIR", "/data/bronze")
    override = Path("/custom/storage")
    assert resolve_storage_dir(override) == override
