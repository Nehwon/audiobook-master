"""Plugin scraper Babelio."""

from __future__ import annotations

from .base_scraper import MetadataSourcePlugin


class BabelioMetadataPlugin(MetadataSourcePlugin):
    name = "babelio"

    def __init__(self, scraper):
        self.scraper = scraper

    def search(self, author: str, title: str):
        return self.scraper.search_babelio(author, title)
