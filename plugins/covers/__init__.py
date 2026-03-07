"""Plugins d'acquisition de covers."""

from .base_cover import CoverProviderPlugin
from .provider_existing_file import ExistingFileCoverProvider
from .provider_url_download import UrlDownloadCoverProvider

__all__ = [
    "CoverProviderPlugin",
    "ExistingFileCoverProvider",
    "UrlDownloadCoverProvider",
]
