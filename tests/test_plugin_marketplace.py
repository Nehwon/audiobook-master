import hashlib
import json
import zipfile
from pathlib import Path

from plugins.marketplace import (
    PluginInstaller,
    PluginRegistryClient,
    PluginRelease,
    is_release_compatible,
)


def test_release_compatibility_rules():
    release = PluginRelease(
        version="1.0.0",
        min_app_version="0.9.0",
        max_app_version="2.0.0",
        package_url="https://example.invalid/plugin.zip",
    )

    assert is_release_compatible("1.5.0", release) is True
    assert is_release_compatible("0.8.9", release) is False
    assert is_release_compatible("2.0.0", release) is False


def test_registry_client_parses_plugins(monkeypatch):
    payload = {
        "plugins": [
            {
                "id": "abs.export",
                "display_name": "ABS Export",
                "description": "Export plugin",
                "releases": [
                    {
                        "version": "1.0.0",
                        "package_url": "https://example.invalid/abs-export-1.0.0.zip",
                    }
                ],
            }
        ]
    }

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    monkeypatch.setattr("plugins.marketplace.urlopen", lambda _url: _Response())

    client = PluginRegistryClient("https://example.invalid/registry.json")
    plugins = client.list_plugins()

    assert len(plugins) == 1
    assert plugins[0].plugin_id == "abs.export"
    assert plugins[0].releases[0].version == "1.0.0"


def test_installer_downloads_and_extracts_zip(monkeypatch, tmp_path: Path):
    zip_path = tmp_path / "plugin.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("plugin.json", '{"name": "abs.export"}')

    zip_bytes = zip_path.read_bytes()
    sha256 = hashlib.sha256(zip_bytes).hexdigest()

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return zip_bytes

    monkeypatch.setattr("plugins.marketplace.urlopen", lambda _url: _Response())

    release = PluginRelease(
        version="1.0.0",
        min_app_version="1.0.0",
        max_app_version="2.0.0",
        package_url="https://example.invalid/plugin.zip",
        sha256=sha256,
    )

    installer = PluginInstaller(install_dir=tmp_path / "installed", app_version="1.5.0")
    installed_path = installer.install("abs.export", release)

    assert (installed_path / "plugin.json").exists()


def test_installer_rejects_bad_checksum(monkeypatch, tmp_path: Path):
    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"not-a-zip-file"

    monkeypatch.setattr("plugins.marketplace.urlopen", lambda _url: _Response())

    release = PluginRelease(
        version="1.0.0",
        min_app_version=None,
        max_app_version=None,
        package_url="https://example.invalid/plugin.zip",
        sha256="deadbeef",
    )

    installer = PluginInstaller(install_dir=tmp_path / "installed", app_version="1.5.0")

    try:
        installer.install("abs.export", release)
        raised = False
    except ValueError:
        raised = True

    assert raised is True
