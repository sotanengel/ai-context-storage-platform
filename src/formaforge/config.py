"""Runtime configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_storage_dir(override: Path | None = None) -> Path:
    """Resolve Bronze storage directory from override, env, or default."""
    if override is not None:
        return override
    if env := os.environ.get("FORMAFORGE_STORAGE_DIR"):
        return Path(env)
    return Path.home() / ".formaforge" / "bronze"
