"""Résolution des chemins runtime partagés entre CLI et Web."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    """Chemins source/sortie/temp/log d'exécution."""

    source: Path
    output: Path
    temp: Path
    log: Path


def resolve_runtime_paths(*, profile: str = "core") -> RuntimePaths:
    """Construit les chemins runtime partagés à partir de l'environnement.

    Priorité des variables d'environnement:
    1) Variables nommées `AUDIOBOOK_*`
    2) Variables historiques (`SOURCE_DIR`, `OUTPUT_DIR`, `TEMP_DIR`, `LOG_DIR`)
    3) Valeurs de fallback selon le profil (`core` ou `web`)
    """

    source_default = os.getenv("AUDIOBOOK_MEDIA_DIR", os.getenv("SOURCE_DIR", "/app/data/source"))
    output_default = os.getenv("AUDIOBOOK_OUTPUT_DIR", os.getenv("OUTPUT_DIR", "/app/data/output"))
    log_default = os.getenv("AUDIOBOOK_LOG_DIR", os.getenv("LOG_DIR", "/app/logs"))

    temp_fallback = "/tmp/audiobooks_web" if profile == "web" else "/tmp/audiobooks"
    temp_default = os.getenv("AUDIOBOOK_TEMP_DIR", os.getenv("TEMP_DIR", temp_fallback))

    return RuntimePaths(
        source=Path(source_default),
        output=Path(output_default),
        temp=Path(temp_default),
        log=Path(log_default),
    )
