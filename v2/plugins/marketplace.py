"""Marketplace de plugins (registre + installation distante)."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import urlopen


@dataclass
class PluginRelease:
    version: str
    min_app_version: Optional[str]
    max_app_version: Optional[str]
    package_url: str
    sha256: Optional[str] = None


@dataclass
class PluginDescriptor:
    plugin_id: str
    display_name: str
    description: str
    releases: List[PluginRelease]


class PluginRegistryClient:
    """Client minimal de lecture de registre JSON distant."""

    def __init__(self, registry_url: str):
        self.registry_url = registry_url

    def fetch(self) -> Dict[str, Any]:
        with urlopen(self.registry_url) as response:  # nosec B310
            payload = response.read().decode("utf-8")
        return json.loads(payload)

    def list_plugins(self) -> List[PluginDescriptor]:
        raw = self.fetch()
        plugins: List[PluginDescriptor] = []
        for item in raw.get("plugins", []):
            releases = [
                PluginRelease(
                    version=release["version"],
                    min_app_version=release.get("min_app_version"),
                    max_app_version=release.get("max_app_version"),
                    package_url=release["package_url"],
                    sha256=release.get("sha256"),
                )
                for release in item.get("releases", [])
            ]
            plugins.append(
                PluginDescriptor(
                    plugin_id=item["id"],
                    display_name=item.get("display_name", item["id"]),
                    description=item.get("description", ""),
                    releases=releases,
                )
            )
        return plugins


def _parse_semver(version: str) -> List[int]:
    core = version.split("-", 1)[0]
    return [int(part) for part in core.split(".") if part.isdigit()]


def _semver_gte(a: str, b: str) -> bool:
    av = _parse_semver(a)
    bv = _parse_semver(b)
    size = max(len(av), len(bv))
    av.extend([0] * (size - len(av)))
    bv.extend([0] * (size - len(bv)))
    return av >= bv


def is_release_compatible(app_version: str, release: PluginRelease) -> bool:
    if release.min_app_version and not _semver_gte(app_version, release.min_app_version):
        return False
    if release.max_app_version and _semver_gte(app_version, release.max_app_version):
        return False
    return True


class PluginInstaller:
    """Prototype d'installation de plugin depuis archive distante (.zip)."""

    def __init__(self, install_dir: Path, app_version: str):
        self.install_dir = Path(install_dir)
        self.app_version = app_version

    def install(self, plugin_id: str, release: PluginRelease) -> Path:
        if not is_release_compatible(self.app_version, release):
            raise ValueError(f"Version incompatible pour {plugin_id}@{release.version}")

        self.install_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="plugin-install-") as tmp_dir:
            archive_path = Path(tmp_dir) / f"{plugin_id}-{release.version}.zip"
            with urlopen(release.package_url) as response, archive_path.open("wb") as handle:  # nosec B310
                handle.write(response.read())

            if release.sha256:
                digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
                if digest.lower() != release.sha256.lower():
                    raise ValueError("Checksum SHA256 invalide")

            target_dir = self.install_dir / plugin_id
            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(archive_path, "r") as archive:
                archive.extractall(target_dir)

        return target_dir
