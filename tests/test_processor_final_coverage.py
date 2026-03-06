"""
Tests étendus pour core/processor.py - Focus sur le coverage des fonctions existantes
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from core.processor import AudiobookProcessor, AudiobookMetadata
from core.config import ProcessingConfig


class TestProcessorFinalCoverage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.output_dir = Path(self.temp_dir) / "output"
        self.temp_dir_path = Path(self.temp_dir) / "temp"
        self.source_dir.mkdir()
        self.output_dir.mkdir()
        self.temp_dir_path.mkdir()
        self.processor = AudiobookProcessor(str(self.source_dir), str(self.output_dir), str(self.temp_dir_path))
        self.processor.config = ProcessingConfig()

    def _fake_run_result(self, returncode=0, stdout="", stderr=""):
        result = MagicMock()
        result.returncode = returncode
        result.stdout = stdout
        result.stderr = stderr
        return result

    def _prepare_audio_files(self, count=1):
        files = []
        for idx in range(count):
            f = self.source_dir / f"audio{idx+1}.mp3"
            f.write_bytes(b"FAKE_AUDIO_DATA")
            files.append(f)
        return files

    def test_convert_to_m4b_pipeline_success(self):
        audio_files = self._prepare_audio_files(2)
        output_file = self.output_dir / "output.m4b"
        metadata = AudiobookMetadata(title="Test", author="Author")

        with patch('subprocess.run', return_value=self._fake_run_result(0)) as mock_run:
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)

        self.assertTrue(result)
        self.assertGreaterEqual(mock_run.call_count, 6)

        loudnorm_present = any('loudnorm=I=-18.0' in ' '.join(call.args[0]) for call in mock_run.call_args_list)
        self.assertTrue(loudnorm_present)

    def test_convert_to_m4b_encode_error(self):
        audio_files = self._prepare_audio_files(1)
        output_file = self.output_dir / "output.m4b"
        metadata = AudiobookMetadata(title="Test", author="Author")

        with patch('subprocess.run', return_value=self._fake_run_result(1, stderr="encode failed")):
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)

        self.assertFalse(result)

    def test_convert_to_m4b_without_chapters(self):
        self.processor.config.enable_chapters = False
        audio_files = self._prepare_audio_files(1)
        output_file = self.output_dir / "output.m4b"
        metadata = AudiobookMetadata(title="Test", author="Author")

        with patch('subprocess.run', return_value=self._fake_run_result(0)) as mock_run:
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)

        self.assertTrue(result)
        final_cmd = mock_run.call_args_list[-1].args[0]
        self.assertNotIn('-map_chapters', final_cmd)

    def test_convert_to_m4b_with_chapters(self):
        self.processor.config.enable_chapters = True
        audio_files = self._prepare_audio_files(1)
        output_file = self.output_dir / "output.m4b"
        metadata = AudiobookMetadata(title="Test", author="Author")

        with patch('subprocess.run', return_value=self._fake_run_result(0)) as mock_run:
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)

        self.assertTrue(result)
        final_cmd = mock_run.call_args_list[-1].args[0]
        self.assertIn('-map_chapters', final_cmd)

if __name__ == '__main__':
    unittest.main()
