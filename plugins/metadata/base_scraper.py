"""Contrat des plugins de scraping de métadonnées."""

from __future__ import annotations


class MetadataSourcePlugin:
    """Contrat minimal d'un plugin de récupération de métadonnées."""

    name: str = ""

    def search(self, author: str, title: str):
        raise NotImplementedError
