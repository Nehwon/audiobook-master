from pathlib import Path

from plugins.exports import AudiobookshelfExportPlugin


class _ClientModern:
    def __init__(self):
        self.called = None

    def upload_audiobook(self, audiobook_path, metadata, library_id=None):
        self.called = (audiobook_path, metadata, library_id)
        return {"id": "item-1"}


class _ClientLegacy:
    def __init__(self):
        self.called = None

    def upload_audiobook(self, audiobook_path, library_id, metadata):
        self.called = (audiobook_path, library_id, metadata)
        return True


def test_export_audiobookshelf_plugin_modern_signature():
    client = _ClientModern()
    plugin = AudiobookshelfExportPlugin(client, "lib-1")

    ok = plugin.export(Path("book.m4b"), {"title": "Book"})

    assert ok is True
    assert client.called[2] == "lib-1"


def test_export_audiobookshelf_plugin_legacy_signature():
    client = _ClientLegacy()
    plugin = AudiobookshelfExportPlugin(client, "lib-2")

    ok = plugin.export(Path("book.m4b"), {"title": "Book"})

    assert ok is True
    assert client.called[1] == "lib-2"
