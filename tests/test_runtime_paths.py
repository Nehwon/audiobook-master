"""Tests pour la résolution des chemins runtime partagés CLI/Web."""

from core.runtime_paths import resolve_runtime_paths


def test_resolve_runtime_paths_core_defaults(monkeypatch):
    for key in (
        "AUDIOBOOK_MEDIA_DIR",
        "AUDIOBOOK_SOURCE_DIR",
        "SOURCE_DIR",
        "AUDIOBOOK_OUTPUT_DIR",
        "OUTPUT_DIR",
        "AUDIOBOOK_TEMP_DIR",
        "TEMP_DIR",
        "AUDIOBOOK_LOG_DIR",
        "LOG_DIR",
    ):
        monkeypatch.delenv(key, raising=False)

    paths = resolve_runtime_paths(profile="core")

    assert str(paths.source) == "/app/data/source"
    assert str(paths.output) == "/app/data/output"
    assert str(paths.temp) == "/tmp/audiobooks"
    assert str(paths.log) == "/app/logs"


def test_resolve_runtime_paths_web_temp_default(monkeypatch):
    monkeypatch.delenv("AUDIOBOOK_TEMP_DIR", raising=False)
    monkeypatch.delenv("TEMP_DIR", raising=False)

    paths = resolve_runtime_paths(profile="web")

    assert str(paths.temp) == "/tmp/audiobooks_web"


def test_resolve_runtime_paths_env_precedence(monkeypatch):
    monkeypatch.setenv("SOURCE_DIR", "/legacy/source")
    monkeypatch.setenv("AUDIOBOOK_MEDIA_DIR", "/modern/source")

    paths = resolve_runtime_paths(profile="core")

    assert str(paths.source) == "/modern/source"


def test_resolve_runtime_paths_prefers_existing_non_empty_legacy_dir(monkeypatch, tmp_path):
    modern = tmp_path / "modern-empty"
    modern.mkdir()
    legacy = tmp_path / "legacy-filled"
    legacy.mkdir()
    (legacy / "book1").mkdir()

    monkeypatch.setenv("AUDIOBOOK_MEDIA_DIR", str(modern))
    monkeypatch.setenv("SOURCE_DIR", str(legacy))

    paths = resolve_runtime_paths(profile="web")

    assert paths.source == legacy


def test_resolve_runtime_paths_supports_audiobook_source_dir_alias(monkeypatch):
    monkeypatch.delenv("AUDIOBOOK_MEDIA_DIR", raising=False)
    monkeypatch.setenv("AUDIOBOOK_SOURCE_DIR", "/alias/source")
    monkeypatch.setenv("SOURCE_DIR", "/legacy/source")

    paths = resolve_runtime_paths(profile="core")

    assert str(paths.source) == "/alias/source"
