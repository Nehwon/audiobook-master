"""Plugin scraper Audible."""

from __future__ import annotations

from .base_scraper import MetadataSourcePlugin


class AudibleMetadataPlugin(MetadataSourcePlugin):
    name = "audible"

    def __init__(self, scraper):
        self.scraper = scraper

    def search(self, author: str, title: str):
        return self.scraper.search_audible(author, title)
