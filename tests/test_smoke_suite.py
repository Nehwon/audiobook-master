"""Suite smoke minimale pour validation rapide P0."""

from core.main import setup_argument_parser
from core.processor import AudiobookProcessor
from integrations.audiobookshelf import AudiobookshelfClient
from web.app import app


def test_smoke_imports_and_parser_defaults(tmp_path):
    parser = setup_argument_parser()
    args = parser.parse_args([])
    assert hasattr(args, "no_ai")
    assert hasattr(args, "no_synopsis")

    processor = AudiobookProcessor(str(tmp_path), str(tmp_path / "out"), str(tmp_path / "tmp"))
    assert processor is not None
    assert AudiobookshelfClient is not None
    assert app is not None
