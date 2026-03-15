"""Provider cover: réutilise un chemin de cover déjà présent."""

from __future__ import annotations

from pathlib import Path

from .base_cover import CoverProviderPlugin


class ExistingFileCoverProvider(CoverProviderPlugin):
    name = "existing_file"

    def fetch(self, metadata, processor) -> str | None:
        cover_path = getattr(metadata, "cover_path", None)
        if cover_path and Path(cover_path).exists():
            return str(cover_path)
        return None
