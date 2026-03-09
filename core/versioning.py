"""Automatic project versioning (M.m.f)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

_VERSION_BASE_FILE = "VERSION_BASE"
_DEFAULT_BASE = "2.2"


def _read_version_base() -> str:
    env_base = (os.getenv("AUDIOBOOK_VERSION_BASE") or "").strip()
    if env_base:
        return env_base

    base_file = Path(__file__).resolve().parent.parent / _VERSION_BASE_FILE
    if base_file.exists():
        value = base_file.read_text(encoding="utf-8").strip()
        if value:
            return value

    return _DEFAULT_BASE


def _read_patch_number() -> int:
    env_patch = (os.getenv("AUDIOBOOK_VERSION_PATCH") or "").strip()
    if env_patch.isdigit():
        return int(env_patch)

    repo_root = Path(__file__).resolve().parent.parent
    try:
        output = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return int(output)
    except Exception:
        return 0


def get_project_version(prefix: str = "v") -> str:
    """Return runtime version in M.m.f format.

    Priority:
    1. AUDIOBOOK_MANAGER_VERSION (explicit override)
    2. Automatic version using VERSION_BASE + git commit count
    """

    explicit = (os.getenv("AUDIOBOOK_MANAGER_VERSION") or "").strip()
    if explicit:
        return explicit

    base = _read_version_base()
    patch = _read_patch_number()
    return f"{prefix}{base}.{patch}"
