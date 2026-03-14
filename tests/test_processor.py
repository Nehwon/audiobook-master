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

    def test_convert_to_m4b_resets_last_error_between_runs(self):
        self.processor.last_error = "old error"
        test_audio = self.source_dir / "reset.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")
        output_path = self.output_dir / "reset.m4b"

        with patch('subprocess.run', return_value=self._mock_run_result(0, stdout='1.0\n')):
            result = self.processor.convert_to_m4b([test_audio], output_path, MagicMock())

        self.assertTrue(result)
        self.assertIsNone(self.processor.last_error)


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

    def test_convert_to_m4b_uses_lossy_utf8_decode_for_subprocess_output(self):
        test_audio = self.source_dir / "accented.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")
        output_path = self.output_dir / "accented.m4b"

        def fake_run(cmd, **kwargs):
            if kwargs.get('text') and kwargs.get('errors') != 'replace':
                raise UnicodeDecodeError('utf-8', b'\xc3', 0, 1, 'invalid continuation byte')

            if cmd and cmd[0] == 'ffprobe':
                return self._mock_run_result(0, stdout='1.0\n')

            return self._mock_run_result(0, stdout='', stderr='ok')

        metadata = MagicMock()
        metadata.get_metadata_dict.return_value = {}

        with patch('subprocess.run', side_effect=fake_run):
            result = self.processor.convert_to_m4b([test_audio], output_path, metadata)

        self.assertTrue(result)

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

    @patch.object(AudiobookProcessor, 'encode_cpu_optimized_phase2', return_value=True)
    def test_process_audiobook_flattens_single_subfolder_with_audio(self, mock_encode):
        book_dir = self.source_dir / "Auteur - Livre"
        child_dir = book_dir / "CD1"
        child_dir.mkdir(parents=True)
        (child_dir / "chapitre1.mp3").write_bytes(b"FAKE_AUDIO_DATA")

        result = self.processor.process_audiobook(book_dir)

        self.assertTrue(result)
        self.assertFalse(child_dir.exists())
        self.assertTrue((book_dir / "chapitre1.mp3").exists())
        mock_encode.assert_called_once()

    @patch.object(AudiobookProcessor, 'encode_cpu_optimized_phase2', return_value=True)
    def test_process_audiobook_emits_corrected_nested_folder_warning(self, mock_encode):
        book_dir = self.source_dir / "Auteur - Livre"
        child_dir = book_dir / "CD1"
        child_dir.mkdir(parents=True)
        (child_dir / "chapitre1.mp3").write_bytes(b"FAKE_AUDIO_DATA")

        progress_events = []
        self.processor.progress_callback = progress_events.append

        result = self.processor.process_audiobook(book_dir)

        self.assertTrue(result)
        corrected_events = [
            event for event in progress_events
            if isinstance(event.get('details'), dict)
            and event['details'].get('code') == 'nested_folder'
            and event['details'].get('status') == 'corrected'
        ]
        self.assertTrue(corrected_events)
        self.assertEqual(corrected_events[0]['details'].get('level'), 'warning')
        mock_encode.assert_called_once()

    def test_process_audiobook_fails_with_nested_subdirectories(self):
        book_dir = self.source_dir / "MonLivre"
        nested_dir = book_dir / "Partie1" / "CD1"
        nested_dir.mkdir(parents=True)
        (nested_dir / "chapitre1.mp3").write_bytes(b"FAKE_AUDIO_DATA")

        result = self.processor.process_audiobook(book_dir)

        self.assertFalse(result)

    def test_process_audiobook_fails_when_no_audio_files(self):
        book_dir = self.source_dir / "MonLivre"
        book_dir.mkdir(parents=True)
        (book_dir / "notes.txt").write_text("pas d'audio")

        result = self.processor.process_audiobook(book_dir)

        self.assertFalse(result)

    def test_process_audiobook_fails_when_m4b_is_present(self):
        book_dir = self.source_dir / "MonLivre"
        book_dir.mkdir(parents=True)
        (book_dir / "book.m4b").write_bytes(b"FAKE_M4B")

        result = self.processor.process_audiobook(book_dir)

        self.assertFalse(result)

    def test_process_all_promotes_grouped_book_folders(self):
        grouped = self.source_dir / "SagaComplete"
        grouped.mkdir(parents=True)

        book1 = grouped / "Auteur A - Livre A"
        book2 = grouped / "Auteur B - Serie 2 - Livre B"
        book1.mkdir()
        book2.mkdir()
        (book1 / "01.mp3").write_bytes(b"FAKE_AUDIO_DATA")
        (book2 / "01.mp3").write_bytes(b"FAKE_AUDIO_DATA")

        with patch.object(self.processor, 'process_audiobook', return_value=True) as mock_process:
            results = self.processor.process_all()

        self.assertEqual(results["success"], 2)
        self.assertEqual(mock_process.call_count, 2)
        self.assertTrue((self.source_dir / "Auteur A - Livre A").exists())
        self.assertTrue((self.source_dir / "Auteur B - Serie 2 - Livre B").exists())

    def test_process_all_fails_on_grouped_nested_subdirectories(self):
        grouped = self.source_dir / "SagaComplete"
        grouped.mkdir(parents=True)

        book1 = grouped / "Auteur A - Livre A" / "CD1"
        book2 = grouped / "Auteur B - Livre B"
        book1.mkdir(parents=True)
        book2.mkdir()
        (book1 / "01.mp3").write_bytes(b"FAKE_AUDIO_DATA")
        (book2 / "01.mp3").write_bytes(b"FAKE_AUDIO_DATA")

        with self.assertRaises(ValueError):
            self.processor.process_all()

    def test_compute_cpu_parallel_tasks_under_8_cores_forces_single_task(self):
        self.assertEqual(self.processor._compute_cpu_parallel_tasks(4), 1)
        self.assertEqual(self.processor._compute_cpu_parallel_tasks(7), 1)

    def test_compute_cpu_parallel_tasks_from_8_cores(self):
        self.assertEqual(self.processor._compute_cpu_parallel_tasks(8), 2)
        self.assertEqual(self.processor._compute_cpu_parallel_tasks(16), 6)

    def test_compute_threads_per_cpu_task(self):
        self.assertEqual(self.processor._compute_threads_per_cpu_task(1), 1)
        self.assertEqual(self.processor._compute_threads_per_cpu_task(8), 2)

    def test_compute_parallel_audiobooks(self):
        self.assertEqual(self.processor._compute_parallel_audiobooks(3), 1)
        self.assertEqual(self.processor._compute_parallel_audiobooks(8), 2)
        self.assertEqual(self.processor._compute_parallel_audiobooks(32), 8)

    def test_normalize_batch_cpu_optimized_emits_progress_events(self):
        aac_temp = self.temp_dir_path / "aac"
        aac_temp.mkdir(parents=True, exist_ok=True)
        aac_files = []
        for idx in range(3):
            src = aac_temp / f"track_{idx+1:04d}.aac"
            src.write_bytes(b"FAKE")
            aac_files.append(src)

        progress_events = []
        self.processor.progress_callback = progress_events.append

        config = MagicMock()
        config.loudnorm_target = -18.0
        config.loudnorm_range = 11.0
        config.loudnorm_true_peak = -1.5

        with patch('subprocess.run', return_value=self._mock_run_result(0)):
            normalized = self.processor.normalize_batch_cpu_optimized(
                aac_files,
                aac_temp,
                config,
                total_cores_override=16,
            )

        self.assertEqual(len(normalized), len(aac_files))
        normalization_events = [
            event for event in progress_events
            if isinstance(event.get('details'), dict)
            and event['details'].get('phase_key') == 'normalization'
        ]
        self.assertTrue(normalization_events)
        self.assertEqual(normalization_events[-1]['details'].get('processed'), len(aac_files))
        self.assertEqual(normalization_events[-1]['details'].get('total'), len(aac_files))

    def test_encode_cpu_optimized_phase2_emits_conversion_and_finalization_progress(self):
        audio_files = []
        for idx in range(2):
            f = self.source_dir / f"track_{idx+1:02d}.mp3"
            f.write_bytes(b"FAKE_AUDIO_DATA")
            audio_files.append(f)

        progress_events = []
        self.processor.progress_callback = progress_events.append

        metadata = MagicMock()
        metadata.get_metadata_dict.return_value = {}

        def fake_encode(task):
            _audio_file, aac_file, _params, _num = task
            Path(aac_file).write_bytes(b"FAKE_AAC")
            return True, Path(aac_file).name, {'action': 'codec_only', 'cpu_threads': 2}

        with patch.object(self.processor, 'analyze_audio_quality', return_value={'codec': 'mp3', 'bitrate': 128, 'sample_rate': 44100}),              patch.object(self.processor, 'encode_single_file_cpu_optimized', side_effect=fake_encode),              patch.object(self.processor, 'detect_cuda_support', return_value=False),              patch.object(self.processor, 'normalize_batch_cpu_optimized', side_effect=lambda aac_files, *_args, **_kwargs: aac_files),              patch('subprocess.run', return_value=self._mock_run_result(0)):
            result = self.processor.encode_cpu_optimized_phase2(audio_files, self.output_dir / 'phase2.m4b', metadata, cpu_budget_cores=8)

        self.assertTrue(result)
        conversion_events = [
            event for event in progress_events
            if isinstance(event.get('details'), dict)
            and event['details'].get('phase_key') == 'conversion'
        ]
        finalization_events = [
            event for event in progress_events
            if isinstance(event.get('details'), dict)
            and event['details'].get('phase_key') == 'finalization'
        ]
        self.assertTrue(conversion_events)
        self.assertTrue(any(evt['details'].get('processed') == len(audio_files) for evt in conversion_events))
        self.assertTrue(finalization_events)
        self.assertEqual(finalization_events[-1]['details'].get('processed'), 2)



if __name__ == '__main__':
    unittest.main()
