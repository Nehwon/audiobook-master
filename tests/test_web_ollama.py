import subprocess
from unittest.mock import patch

import pytest

from web.app import _run_ollama_command


def test_run_ollama_command_missing_binary_raises_runtime_error():
    with patch("web.app.subprocess.run", side_effect=FileNotFoundError("ollama")):
        with pytest.raises(RuntimeError, match="Commande 'ollama' introuvable"):
            _run_ollama_command(["list"])


def test_run_ollama_command_returns_completed_process():
    completed = subprocess.CompletedProcess(args=["ollama", "list"], returncode=0, stdout="ok", stderr="")
    with patch("web.app.subprocess.run", return_value=completed):
        result = _run_ollama_command(["list"])

    assert result.returncode == 0
    assert result.stdout == "ok"
