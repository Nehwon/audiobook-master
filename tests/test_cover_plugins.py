from pathlib import Path
from types import SimpleNamespace

from plugins.covers import ExistingFileCoverProvider, UrlDownloadCoverProvider


class _Resp:
    def __init__(self, content=b"img"):
        self.content = content

    def raise_for_status(self):
        return None


def test_existing_file_cover_provider(tmp_path):
    cover = tmp_path / "cover.jpg"
    cover.write_bytes(b"img")
    provider = ExistingFileCoverProvider()

    metadata = SimpleNamespace(cover_path=str(cover), cover_url=None)
    result = provider.fetch(metadata, processor=SimpleNamespace(temp_dir=str(tmp_path)))

    assert result == str(cover)


def test_url_download_cover_provider(tmp_path, monkeypatch):
    provider = UrlDownloadCoverProvider()

    def _fake_get(url, timeout=10):
        return _Resp(b"cover-bytes")

    monkeypatch.setattr("plugins.covers.provider_url_download.requests.get", _fake_get)
    metadata = SimpleNamespace(cover_path=None, cover_url="http://example.com/cover.jpg")
    result = provider.fetch(metadata, processor=SimpleNamespace(temp_dir=str(tmp_path)))

    assert result is not None
    assert Path(result).exists()
    assert Path(result).read_bytes() == b"cover-bytes"
