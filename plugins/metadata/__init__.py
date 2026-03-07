"""Plugins de récupération de métadonnées externes."""

from .base_scraper import MetadataSourcePlugin
from .scraper_google_books import GoogleBooksMetadataPlugin
from .scraper_audible import AudibleMetadataPlugin
from .scraper_babelio import BabelioMetadataPlugin

__all__ = [
    "MetadataSourcePlugin",
    "GoogleBooksMetadataPlugin",
    "AudibleMetadataPlugin",
    "BabelioMetadataPlugin",
]
