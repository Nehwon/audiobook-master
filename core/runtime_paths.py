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


def _first_non_empty_env(*keys: str) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
    return None


def _select_path(*, env_keys: tuple[str, ...], fallback: str) -> Path:
    """Sélectionne un chemin d'env de façon robuste pour les upgrades.

    Stratégie:
    1) Si un chemin configuré existe et contient déjà des éléments, il est prioritaire.
    2) Sinon, premier chemin configuré existant.
    3) Sinon, première valeur d'environnement non vide.
    4) Sinon, fallback.

    Cela évite de choisir un chemin "moderne" vide (ex: dossier recréé) alors que
    le dossier legacy monté contient déjà les médias utilisateur.
    """

    candidates: list[Path] = []
    for key in env_keys:
        value = os.getenv(key)
        if value and value.strip():
            candidates.append(Path(value.strip()))

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            try:
                if any(candidate.iterdir()):
                    return candidate
            except OSError:
                continue

    for candidate in candidates:
        if candidate.exists():
            return candidate

    if candidates:
        return candidates[0]

    return Path(fallback)


def resolve_runtime_paths(*, profile: str = "core") -> RuntimePaths:
    """Construit les chemins runtime partagés à partir de l'environnement.

    Priorité des variables d'environnement:
    1) Variables nommées `AUDIOBOOK_*`
    2) Variables historiques (`SOURCE_DIR`, `OUTPUT_DIR`, `TEMP_DIR`, `LOG_DIR`)
    3) Valeurs de fallback selon le profil (`core` ou `web`)
    """

    source_default = "/app/data/source"
    output_default = "/app/data/output"
    log_default = "/app/logs"

    temp_fallback = "/tmp/audiobooks_web" if profile == "web" else "/tmp/audiobooks"

    return RuntimePaths(
        source=_select_path(
            env_keys=("AUDIOBOOK_MEDIA_DIR", "AUDIOBOOK_SOURCE_DIR", "SOURCE_DIR"),
            fallback=source_default,
        ),
        output=_select_path(
            env_keys=("AUDIOBOOK_OUTPUT_DIR", "OUTPUT_DIR"),
            fallback=output_default,
        ),
        temp=Path(_first_non_empty_env("AUDIOBOOK_TEMP_DIR", "TEMP_DIR") or temp_fallback),
        log=Path(_first_non_empty_env("AUDIOBOOK_LOG_DIR", "LOG_DIR") or log_default),
    )
