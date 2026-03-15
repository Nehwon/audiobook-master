"""Contrat des plugins de covers."""

from __future__ import annotations


class CoverProviderPlugin:
    """Contrat minimal pour un fournisseur de couverture."""

    name: str = ""

    def fetch(self, metadata, processor) -> str | None:
        raise NotImplementedError
