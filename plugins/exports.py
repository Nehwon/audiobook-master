"""Plugins d'export (publication vers des services externes)."""

from pathlib import Path
from typing import Any, Dict, Optional


class AudiobookshelfExportPlugin:
    """Plugin d'export Audiobookshelf avec compat signatures legacy/modernes."""

    name = "audiobookshelf"

    def __init__(self, client: Any, library_id: Optional[str] = None):
        self.client = client
        self.library_id = library_id

    def export(self, audiobook_path: Path, metadata: Dict[str, Any]) -> bool:
        """Upload un audiobook en tolérant les signatures historiques du client.

        Signatures supportées:
        - moderne: upload_audiobook(path, metadata, library_id=None)
        - legacy:  upload_audiobook(path, library_id, metadata)
        """
        upload_method = getattr(self.client, "upload_audiobook", None)
        if not callable(upload_method):
            return False

        # Signature moderne (historique courant du client)
        try:
            result = upload_method(audiobook_path, metadata, library_id=self.library_id)
            return bool(result)
        except TypeError:
            pass

        # Signature legacy (tests de non-régression)
        try:
            result = upload_method(audiobook_path, self.library_id, metadata)
            return bool(result)
        except TypeError:
            return False
