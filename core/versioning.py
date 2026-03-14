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


def _normalize_base(base: str) -> tuple[int, int, int]:
    """Normalize base version into ``(major, minor, patch_seed)``.

    Accepted formats:
    - M.m
    - M.m.p
    Any invalid value falls back to ``_DEFAULT_BASE`` and seed ``0``.
    """

    parts = [part.strip() for part in base.split(".") if part.strip()]
    if len(parts) not in {2, 3} or not all(part.isdigit() for part in parts):
        parts = _DEFAULT_BASE.split(".")

    major = int(parts[0])
    minor = int(parts[1])
    patch_seed = int(parts[2]) if len(parts) == 3 else 0
    return major, minor, patch_seed


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
    major, minor, patch_seed = _normalize_base(base)
    patch = patch_seed + _read_patch_number()
    return f"{prefix}{major}.{minor}.{patch}"
