#!/usr/bin/env python3
"""Outils de diagnostic CLI pour Audiobook Master."""

from __future__ import annotations

import importlib
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, Any

from .config import ProcessingConfig


CHECKED_MODULES = [
    "requests",
    "bs4",
    "PIL",
    "mutagen",
    "flask",
]

CHECKED_BINARIES = [
    "ffmpeg",
    "ollama",
]

CHECKED_ENV_VARS = [
    "AUDIOBOOKSHELF_HOST",
    "AUDIOBOOKSHELF_PORT",
    "AUDIOBOOKSHELF_USERNAME",
    "AUDIOBOOKSHELF_TOKEN",
    "AUDIOBOOKSHELF_LIBRARY_ID",
]


def _safe_path_status(path_value: str) -> Dict[str, Any]:
    path = Path(path_value)
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "readable": os.access(path, os.R_OK),
        "writable": os.access(path, os.W_OK),
    }


def collect_diagnostics(config: ProcessingConfig) -> Dict[str, Any]:
    """Collecte un état synthétique de l'environnement d'exécution."""
    modules = {}
    for module_name in CHECKED_MODULES:
        try:
            importlib.import_module(module_name)
            modules[module_name] = "ok"
        except Exception as exc:  # noqa: BLE001
            modules[module_name] = f"missing: {exc}"

    binaries = {binary: shutil.which(binary) for binary in CHECKED_BINARIES}

    directories = {
        "source": _safe_path_status(config.source_directory),
        "output": _safe_path_status(config.output_directory),
        "temp": _safe_path_status(config.temp_directory),
    }

    env = {
        key: ("set" if os.getenv(key) else "unset")
        for key in CHECKED_ENV_VARS
    }

    return {
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
        },
        "dependencies": modules,
        "binaries": binaries,
        "directories": directories,
        "environment": env,
        "config": {
            "enable_scraping": config.enable_scraping,
            "enable_synopsis_generation": config.enable_synopsis_generation,
            "enable_upload": config.enable_upload,
            "audio_bitrate": config.audio_bitrate,
            "sample_rate": config.sample_rate,
        },
    }


def print_diagnostics_report(diagnostics: Dict[str, Any]) -> None:
    """Affiche un rapport lisible en console."""
    print("=== Audiobook Master Diagnostic ===")
    print(f"Python: {diagnostics['python']['version']} ({diagnostics['python']['executable']})")
    print(f"Plateforme: {diagnostics['platform']['system']} {diagnostics['platform']['release']}")

    print("\n[Dependances Python]")
    for module_name, status in diagnostics["dependencies"].items():
        print(f"- {module_name}: {status}")

    print("\n[Binaires systeme]")
    for binary, path in diagnostics["binaries"].items():
        print(f"- {binary}: {path or 'missing'}")

    print("\n[Repertoires]")
    for name, info in diagnostics["directories"].items():
        print(
            f"- {name}: {info['path']} "
            f"(exists={info['exists']}, readable={info['readable']}, writable={info['writable']})"
        )

    print("\n[Variables d'environnement]")
    for key, value in diagnostics["environment"].items():
        print(f"- {key}: {value}")

    print("\n[Configuration active]")
    for key, value in diagnostics["config"].items():
        print(f"- {key}: {value}")


def diagnostics_to_json(diagnostics: Dict[str, Any]) -> str:
    return json.dumps(diagnostics, indent=2, ensure_ascii=False)
