from core.versioning import get_project_version


def test_get_project_version_default_format():
    version = get_project_version()
    assert version.startswith("v")
    parts = version[1:].split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
