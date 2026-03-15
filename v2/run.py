#!/usr/bin/env python3
"""Compatibilité CLI legacy.

Ce script conserve l'entrée historique ``run.py`` mais délègue entièrement
vers l'implémentation active ``core.main``.
"""

from __future__ import annotations

import logging
import sys

from core.main import main as core_main

LOGGER = logging.getLogger("audiobook.legacy.run")


def _setup_logging() -> None:
    """Configure un logging minimal pour le wrapper de compatibilité."""
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> int:
    """Délègue vers ``core.main.main`` en conservant l'interface historique."""
    _setup_logging()
    LOGGER.warning("`run.py` est déprécié: utilisez `python -m core.main`.")
    try:
        core_main()
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
