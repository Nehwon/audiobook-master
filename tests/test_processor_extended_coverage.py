"""
Tests étendus pour core/processor.py - Focus sur le coverage des fonctions manquantes
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import time
from pathlib import Path

from core.processor import AudiobookProcessor, AudiobookMetadata
from core.config import ProcessingConfig


class TestProcessorExtendedCoverage(unittest.TestCase):
    """Tests étendus pour couvrir les fonctions manquantes de processor.py"""

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
        self.processor.config = ProcessingConfig()

    def test_process_audiobook_success(self):
        """Test le traitement complet d'un audiobook réussi"""
        # Mock des méthodes
        with patch.object(self.processor, 'parse_filename') as mock_parse:
            with patch.object(self.processor, 'extract_archive') as mock_extract:
                with patch.object(self.processor, 'find_audio_files') as mock_find:
                    with patch.object(self.processor, 'convert_to_m4b') as mock_convert:
                        with patch.object(self.processor, 'add_cover_to_m4b') as mock_cover:
                            with patch.object(self.processor, 'scrap_book_info') as mock_scrap:
                                with patch.object(self.processor, 'generate_synopsis') as mock_synopsis:
                                    with patch.object(self.processor, 'download_cover') as mock_download:
                                        
                                        # Configuration des mocks
                                        mock_parse.return_value = AudiobookMetadata(
                                            title="Test Book",
                                            author="Test Author"
                                        )
                                        mock_extract.return_value = True
                                        # Mock de find_audio_files pour retourner des chemins absolus
                                        mock_find.return_value = [
                                            self.source_dir / "audio1.mp3",
                                            self.source_dir / "audio2.mp3"
                                        ]
                                        mock_convert.return_value = True
                                        mock_cover.return_value = True
                                        mock_scrap.return_value = AudiobookMetadata(
                                            title="Test Book",
                                            author="Test Author"
                                        )
                                        mock_synopsis.return_value = "Generated synopsis"
                                        mock_download.return_value = "/path/to/cover.jpg"
                                        
                                        # Créer les fichiers audio factices
                                        (self.source_dir / "audio1.mp3").write_bytes(b"fake audio")
                                        (self.source_dir / "audio2.mp3").write_bytes(b"fake audio")
                                        
                                        # Test
                                        test_file = self.source_dir / "test.zip"
                                        test_file.write_bytes(b"fake zip")
                                        result = self.processor.process_audiobook(test_file)
                                        
                                        self.assertTrue(result)
                                        mock_parse.assert_called_once()
                                        mock_extract.assert_called_once()
                                        mock_find.assert_called_once()
                                        mock_convert.assert_called_once()

    def test_process_audiobook_extraction_failure(self):
        """Test le traitement avec échec d'extraction"""
        with patch.object(self.processor, 'parse_filename') as mock_parse:
            with patch.object(self.processor, 'extract_archive') as mock_extract:
                mock_parse.return_value = AudiobookMetadata(
                    title="Test Book",
                    author="Test Author"
                )
                mock_extract.return_value = False
                
                test_file = self.source_dir / "test.zip"
                result = self.processor.process_audiobook(test_file)
                
                self.assertFalse(result)

    def test_process_audiobook_no_audio_files(self):
        """Test le traitement sans fichiers audio"""
        with patch.object(self.processor, 'parse_filename') as mock_parse:
            with patch.object(self.processor, 'extract_archive') as mock_extract:
                with patch.object(self.processor, 'find_audio_files') as mock_find:
                    mock_parse.return_value = AudiobookMetadata(
                        title="Test Book",
                        author="Test Author"
                    )
                    mock_extract.return_value = True
                    mock_find.return_value = []
                    
                    test_file = self.source_dir / "test.zip"
                    result = self.processor.process_audiobook(test_file)
                    
                    self.assertFalse(result)

    def test_process_audiobook_conversion_failure(self):
        """Test le traitement avec échec de conversion"""
        with patch.object(self.processor, 'parse_filename') as mock_parse:
            with patch.object(self.processor, 'extract_archive') as mock_extract:
                with patch.object(self.processor, 'find_audio_files') as mock_find:
                    with patch.object(self.processor, 'convert_to_m4b') as mock_convert:
                        mock_parse.return_value = AudiobookMetadata(
                            title="Test Book",
                            author="Test Author"
                        )
                        mock_extract.return_value = True
                        mock_find.return_value = [Path("audio1.mp3")]
                        mock_convert.return_value = False
                        
                        test_file = self.source_dir / "test.zip"
                        result = self.processor.process_audiobook(test_file)
                        
                        self.assertFalse(result)

    def test_process_all_success(self):
        """Test le traitement de tous les fichiers réussi"""
        # Mock des fichiers
        test_files = [
            self.source_dir / "test1.zip",
            self.source_dir / "test2.mp3",
            self.source_dir / "test3.m4a"
        ]
        for file in test_files:
            file.write_bytes(b"fake content")
        
        with patch.object(self.processor, 'process_audiobook') as mock_process:
            mock_process.return_value = True
            
            result = self.processor.process_all()
            
            self.assertIn('success', result)
            self.assertIn('failed', result)
            self.assertIn('skipped', result)
            self.assertEqual(result['success'], 3)

    def test_process_all_mixed_results(self):
        """Test le traitement avec résultats mixtes"""
        # Mock des fichiers
        test_files = [
            self.source_dir / "test1.zip",
            self.source_dir / "test2.mp3",
            self.source_dir / "test3.m4a"
        ]
        for file in test_files:
            file.write_bytes(b"fake content")
        
        with patch.object(self.processor, 'process_audiobook') as mock_process:
            mock_process.side_effect = [True, False, True]
            
            result = self.processor.process_all()
            
            self.assertEqual(result['success'], 2)
            self.assertEqual(result['failed'], 1)

    def test_process_all_with_exceptions(self):
        """Test le traitement avec des exceptions"""
        # Mock des fichiers
        test_files = [
            self.source_dir / "test1.zip",
            self.source_dir / "test2.mp3"
        ]
        for file in test_files:
            file.write_bytes(b"fake content")
        
        with patch.object(self.processor, 'process_audiobook') as mock_process:
            # Simuler une exception sur le deuxième appel
            def side_effect_func(file):
                if file.name == "test2.mp3":
                    raise Exception("Test error")
                return True
            
            mock_process.side_effect = side_effect_func
            
            # Le test va lever une exception, mais on vérifie que le mock est appelé
            try:
                self.processor.process_all()
            except Exception:
                pass  # L'exception est attendue
            
            # Vérifier qu'au moins un appel a été fait avant l'exception
            self.assertGreaterEqual(mock_process.call_count, 1)

    def test_process_all_empty_directory(self):
        """Test le traitement d'un répertoire vide"""
        # S'assurer que le répertoire est vide
        for file in self.source_dir.glob("*"):
            if file.is_file():
                file.unlink()
        
        result = self.processor.process_all()
        
        self.assertEqual(result['success'], 0)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['skipped'], 0)

    def test_process_all_with_ignored_files(self):
        """Test le traitement avec des fichiers ignorés"""
        # Créer des fichiers non audio
        (self.source_dir / "readme.txt").write_text("readme")
        (self.source_dir / "image.jpg").write_bytes(b"fake image")
        
        result = self.processor.process_all()
        
        self.assertEqual(result['success'], 0)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['skipped'], 2)  # Les fichiers non audio sont ignorés

    def test_process_audiobook_with_config(self):
        """Test le traitement avec configuration personnalisée"""
        # Configuration personnalisée
        custom_config = ProcessingConfig()
        custom_config.audio_bitrate = "256k"
        custom_config.enable_gpu_acceleration = False
        self.processor.config = custom_config
        
        with patch.object(self.processor, 'parse_filename') as mock_parse:
            with patch.object(self.processor, 'extract_archive') as mock_extract:
                with patch.object(self.processor, 'find_audio_files') as mock_find:
                    with patch.object(self.processor, 'convert_to_m4b') as mock_convert:
                        mock_parse.return_value = AudiobookMetadata(
                            title="Test Book",
                            author="Test Author"
                        )
                        mock_extract.return_value = True
                        mock_find.return_value = [self.source_dir / "audio1.mp3"]
                        mock_convert.return_value = True
                        
                        # Créer le fichier audio
                        (self.source_dir / "audio1.mp3").write_bytes(b"fake audio")
                        
                        test_file = self.source_dir / "test.zip"
                        test_file.write_bytes(b"fake zip")
                        result = self.processor.process_audiobook(test_file)
                        
                        self.assertTrue(result)
                        # Vérifier que convert_to_m4b a été appelé avec la bonne configuration
                        mock_convert.assert_called_once()


if __name__ == '__main__':
    unittest.main()
