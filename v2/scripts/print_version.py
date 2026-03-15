#!/usr/bin/env python3
"""Print resolved Audiobook Master version (M.m.f)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.versioning import get_project_version


if __name__ == "__main__":
    print(get_project_version())
