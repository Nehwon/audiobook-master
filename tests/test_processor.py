"""
Tests unitaires pour core/processor.py
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import time
import subprocess
from pathlib import Path

from core.processor import AudiobookProcessor


class TestAudiobookProcessor(unittest.TestCase):
    """Tests pour la classe AudiobookProcessor"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.output_dir = Path(self.temp_dir) / "output"
        self.temp_dir_path = Path(self.temp_dir) / "temp"

        self.source_dir.mkdir()
        self.output_dir.mkdir()
        self.temp_dir_path.mkdir()

        self.processor = AudiobookProcessor(
            str(self.source_dir),
            str(self.output_dir),
            str(self.temp_dir_path)
        )

    def test_convert_to_m4b_timeout_handling(self):
        """Teste la gestion du timeout dans convert_to_m4b"""
        # Crée un fichier audio factice
        test_audio = self.source_dir / "test.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")

        # Crée un fichier de sortie factice
        output_path = self.output_dir / "output.m4b"

        # Simule un processus FFmpeg qui ne se termine jamais
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Processus toujours en cours

        # Remplace subprocess.Popen pour retourner notre mock
        with patch('subprocess.Popen', return_value=mock_process):
            with patch('time.time') as mock_time:
                # Configure time.time pour simuler un dépassement de timeout
                # Premier appel: start_loop_time = 0
                # Deuxième appel: current_time = 15000 (> 14400)
                mock_time.side_effect = [0, 15000]
                
                # Teste la conversion - doit lever une exception de timeout
                with self.assertRaises(Exception):
                    self.processor.convert_to_m4b([test_audio], output_path, MagicMock())

    def test_convert_to_m4b_normal_completion(self):
        """Teste une conversion normale qui se termine correctement"""
        # Crée un fichier audio factice
        test_audio = self.source_dir / "test.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")

        # Crée un fichier de sortie factice
        output_path = self.output_dir / "output.m4b"

        # Simule un processus FFmpeg qui se termine rapidement
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]  # Se termine au 2ème appel
        mock_process.returncode = 0
        mock_process.communicate.return_value = ("output", "")

        # Remplace subprocess.Popen pour retourner notre mock
        with patch('subprocess.Popen', return_value=mock_process):
            # Exécute la conversion
            result = self.processor.convert_to_m4b([test_audio], output_path, MagicMock())

            # Vérifie que la conversion a réussi
            self.assertTrue(result)
            
            # Vérifie que le processus a été correctement géré
            mock_process.communicate.assert_called_once()

    def test_convert_to_m4b_error_handling(self):
        """Teste la gestion des erreurs dans convert_to_m4b"""
        # Crée un fichier audio factice
        test_audio = self.source_dir / "test.mp3"
        test_audio.write_bytes(b"FAKE_AUDIO_DATA")

        # Crée un fichier de sortie factice
        output_path = self.output_dir / "output.m4b"

        # Simule un processus FFmpeg qui échoue
        mock_process = MagicMock()
        mock_process.poll.return_value = 0  # Processus terminé
        mock_process.returncode = 1  # Code de retour indiquant une erreur
        mock_process.communicate.return_value = ("", "ERROR: FFmpeg failed")

        # Remplace subprocess.Popen pour retourner notre mock
        with patch('subprocess.Popen', return_value=mock_process):
            # Teste la conversion - doit retourner False en cas d'erreur
            result = self.processor.convert_to_m4b([test_audio], output_path, MagicMock())

            # Vérifie que la conversion échoue
            self.assertFalse(result)

    def test_ffmpeg_concat_file_entry_escapes_single_quotes(self):
        """Teste l'échappement des apostrophes dans la filelist concat FFmpeg."""
        audio_file = self.source_dir / "d'ouverture" / "01 Credits d'ouverture.mp3"
        audio_file.parent.mkdir(parents=True, exist_ok=True)
        audio_file.write_bytes(b"FAKE_AUDIO_DATA")

        entry = self.processor._ffmpeg_concat_file_entry(audio_file)

        self.assertTrue(entry.startswith("file '"))
        self.assertTrue(entry.endswith("'\n"))
        self.assertIn(r"d'\''ouverture", entry)


    def test_process_audiobook_fails_when_subdirectories_exist(self):
        """Teste l'échec si le dossier contient des sous-dossiers."""
        book_dir = self.source_dir / "MonLivre"
        nested_dir = book_dir / "SousDossier"
        nested_dir.mkdir(parents=True)
        (nested_dir / "chapitre1.mp3").write_bytes(b"FAKE_AUDIO_DATA")

        result = self.processor.process_audiobook(book_dir)

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
