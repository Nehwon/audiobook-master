"""
Tests unitaires pour core/processor.py
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from core.processor import AudiobookProcessor


class TestAudiobookProcessor(unittest.TestCase):
    """Tests pour la classe AudiobookProcessor"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.output_dir = Path(self.temp_dir) / "output"
        self.temp_dir_path = Path(self.temp_dir) / "temp"
        self.source_dir.mkdir()
        self.output_dir.mkdir()
        self.temp_dir_path.mkdir()
        self.processor = AudiobookProcessor(str(self.source_dir), str(self.output_dir), str(self.temp_dir_path))

    def _mock_run_result(self, returncode=0, stdout="", stderr=""):
        result = MagicMock()
        result.returncode = returncode
        result.stdout = stdout
        result.stderr = stderr
        return result

    def test_convert_to_m4b_normal_completion(self):
        test_audio = self.source_dir / "test.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")
        output_path = self.output_dir / "output.m4b"

        with patch('subprocess.run', return_value=self._mock_run_result(0)):
            result = self.processor.convert_to_m4b([test_audio], output_path, MagicMock())

        self.assertTrue(result)

    def test_convert_to_m4b_error_handling(self):
        test_audio = self.source_dir / "test.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")
        output_path = self.output_dir / "output.m4b"

        with patch('subprocess.run', return_value=self._mock_run_result(1, stderr="ERROR: FFmpeg failed")):
            result = self.processor.convert_to_m4b([test_audio], output_path, MagicMock())

        self.assertFalse(result)

    def test_convert_to_m4b_does_not_use_progress_pipe(self):
        test_audio = self.source_dir / "test_progress.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")
        output_path = self.output_dir / "output_progress.m4b"

        with patch('subprocess.run', return_value=self._mock_run_result(0)) as mock_run:
            self.processor.convert_to_m4b([test_audio], output_path, MagicMock())

        all_cmds = [call.args[0] for call in mock_run.call_args_list]
        flattened = [item for cmd in all_cmds for item in cmd]
        self.assertNotIn('-progress', flattened)
        self.assertNotIn('pipe:1', flattened)

    def test_ffmpeg_concat_file_entry_escapes_single_quotes(self):
        audio_file = self.source_dir / "d'ouverture" / "01 Credits d'ouverture.mp3"
        audio_file.parent.mkdir(parents=True, exist_ok=True)
        audio_file.write_bytes(b"FAKE_AUDIO_DATA")

        entry = self.processor._ffmpeg_concat_file_entry(audio_file)

        self.assertTrue(entry.startswith("file '"))
        self.assertTrue(entry.endswith("'\n"))
        self.assertIn(r"d'\''ouverture", entry)

    def test_process_audiobook_fails_when_subdirectories_exist(self):
        book_dir = self.source_dir / "MonLivre"
        nested_dir = book_dir / "SousDossier"
        nested_dir.mkdir(parents=True)
        (nested_dir / "chapitre1.mp3").write_bytes(b"FAKE_AUDIO_DATA")

        result = self.processor.process_audiobook(book_dir)

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
