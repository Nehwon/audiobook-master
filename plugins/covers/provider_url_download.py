"""Provider cover: télécharge depuis `metadata.cover_url`."""

from __future__ import annotations

import hashlib
from pathlib import Path

import requests

from .base_cover import CoverProviderPlugin


class UrlDownloadCoverProvider(CoverProviderPlugin):
    name = "url_download"

    def fetch(self, metadata, processor) -> str | None:
        cover_url = getattr(metadata, "cover_url", None)
        if not cover_url:
            return None

        temp_dir = Path(getattr(processor, "temp_dir", "/tmp/audiobooks")) / "covers"
        temp_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha1(cover_url.encode("utf-8")).hexdigest()[:16]
        output_path = temp_dir / f"cover_{digest}.jpg"

        try:
            response = requests.get(cover_url, timeout=10)
            response.raise_for_status()
            output_path.write_bytes(response.content)
            return str(output_path)
        except Exception:
            return None
