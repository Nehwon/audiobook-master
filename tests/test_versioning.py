from core.versioning import get_project_version


def test_get_project_version_default_format():
    version = get_project_version()
    assert version.startswith("v")
    parts = version[1:].split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_get_project_version_supports_two_part_base(monkeypatch):
    monkeypatch.setenv("AUDIOBOOK_VERSION_BASE", "2.2")
    monkeypatch.setenv("AUDIOBOOK_VERSION_PATCH", "5")
    monkeypatch.delenv("AUDIOBOOK_MANAGER_VERSION", raising=False)

    assert get_project_version() == "v2.2.5"


def test_get_project_version_supports_three_part_base(monkeypatch):
    monkeypatch.setenv("AUDIOBOOK_VERSION_BASE", "1.4.10")
    monkeypatch.setenv("AUDIOBOOK_VERSION_PATCH", "7")
    monkeypatch.delenv("AUDIOBOOK_MANAGER_VERSION", raising=False)

    assert get_project_version() == "v1.4.17"
