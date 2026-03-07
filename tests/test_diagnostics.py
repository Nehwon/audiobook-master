import json
from core.config import ProcessingConfig
from core.diagnostics import collect_diagnostics, diagnostics_to_json
from core.main import setup_argument_parser


def test_setup_argument_parser_has_diagnostic_flags():
    parser = setup_argument_parser()
    args = parser.parse_args(["--diagnostic-json"])
    assert args.diagnostic_json is True
    assert args.diagnostic is False


def test_collect_diagnostics_returns_expected_sections(tmp_path):
    config = ProcessingConfig(
        source_directory=str(tmp_path / "src"),
        output_directory=str(tmp_path / "out"),
        temp_directory=str(tmp_path / "tmp"),
    )

    report = collect_diagnostics(config)

    assert "dependencies" in report
    assert "binaries" in report
    assert "directories" in report
    assert "environment" in report
    assert report["directories"]["source"]["exists"] is True


def test_diagnostics_json_is_valid(tmp_path):
    config = ProcessingConfig(
        source_directory=str(tmp_path / "src"),
        output_directory=str(tmp_path / "out"),
        temp_directory=str(tmp_path / "tmp"),
    )
    content = diagnostics_to_json(collect_diagnostics(config))
    payload = json.loads(content)
    assert "python" in payload
    assert "config" in payload
