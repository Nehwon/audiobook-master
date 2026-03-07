#!/usr/bin/env python3
"""Compatibilité launcher web legacy.

Ce script conserve l'entrée historique ``start_web.py`` mais délègue
vers l'application web active ``web.app``.
"""

from __future__ import annotations

import logging
import os
import sys

from web.app import app

LOGGER = logging.getLogger("audiobook.legacy.web")


def _setup_logging() -> None:
    """Configure un logging minimal pour le wrapper de compatibilité."""
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> int:
    """Démarre Flask via l'application active ``web.app``."""
    _setup_logging()
    LOGGER.warning("`start_web.py` est déprécié: utilisez `python -m web.app`.")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") in {"1", "true", "True"}

    app.run(host=host, port=port, debug=debug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
