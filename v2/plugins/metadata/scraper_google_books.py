"""Plugin scraper Google Books."""

from __future__ import annotations

from .base_scraper import MetadataSourcePlugin


class GoogleBooksMetadataPlugin(MetadataSourcePlugin):
    name = "google_books"

    def __init__(self, scraper):
        self.scraper = scraper

    def search(self, author: str, title: str):
        return self.scraper.search_google_books(author, title)
