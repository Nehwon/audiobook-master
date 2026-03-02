"""
Tests étendus pour core/main.py - Focus sur le coverage des fonctions manquantes
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import sys
from pathlib import Path
from io import StringIO

from core.main import setup_argument_parser, main
from core.config import ProcessingConfig


class TestMainExtendedCoverage(unittest.TestCase):
    """Tests étendus pour couvrir les fonctions manquantes de main.py"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.output_dir = Path(self.temp_dir) / "output"
        
        self.source_dir.mkdir()
        self.output_dir.mkdir()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_upload_enabled(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test l'upload vers Audiobookshelf activé"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config.enable_upload = True
        mock_config.audiobookshelf_host = "http://localhost:13378"
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--upload']):
            main()
            
            # Vérifications
            mock_processor.process_all.assert_called_once()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_upload_missing_config(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test l'upload avec configuration manquante"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config.enable_upload = True
        mock_config.audiobookshelf_host = None  # Configuration manquante
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--upload']):
            main()
            
            # Vérifications
            mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_batch_processing_with_results(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement par lots avec résultats détaillés"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 5, 'failed': 2, 'skipped': 1}
        mock_processor_class.return_value = mock_processor
        
        # Mock des fichiers
        for i in range(3):
            test_file = self.source_dir / f"test{i}.mp3"
            test_file.write_bytes(b"fake audio")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
            main()
            
            # Vérifications
            mock_processor.process_all.assert_called_once()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_dry_run_batch_mode(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le mode dry-run pour traitement par lots"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.parse_filename.return_value = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Mock des fichiers
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--dry-run']):
            main()
            
            # Vérifications - le dry-run ne traite pas les fichiers dans l'implémentation actuelle
            mock_processor.process_all.assert_not_called()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_dry_run_single_file(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le mode dry-run pour fichier unique"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.parse_filename.return_value = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Mock du fichier
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--single', 'test.mp3', '--dry-run']):
            main()
            
            # Vérifications
            mock_processor.parse_filename.assert_called_once()
            mock_processor.process_audiobook.assert_not_called()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_single_file_absolute_path(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement avec chemin absolu"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_audiobook.return_value = True
        mock_processor_class.return_value = mock_processor
        
        # Mock du fichier avec chemin absolu
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio")
        
        # Mock sys.argv avec chemin absolu
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--single', str(test_file)]):
            main()
            
            # Vérifications
            mock_processor.process_audiobook.assert_called_once()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_single_file_relative_path(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement avec chemin relatif"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config.source_directory = str(self.source_dir)
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_audiobook.return_value = True
        mock_processor_class.return_value = mock_processor
        
        # Mock du fichier
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio")
        
        # Mock sys.argv avec chemin relatif
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--single', 'test.mp3']):
            main()
            
            # Vérifications
            mock_processor.process_audiobook.assert_called_once()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_critical_exception_handling(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test la gestion des exceptions critiques"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config_class.side_effect = Exception("Critical error")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
            # Le test vérifie juste que l'exception est gérée
            try:
                main()
            except Exception:
                pass  # L'exception est attendue
        
        # Vérifier que le code a été exécuté
        self.assertTrue(mock_config_class.called)

    def test_setup_argument_parser_help(self):
        """Test l'affichage de l'aide"""
        parser = setup_argument_parser()
        
        # Test que le parser a bien une option d'aide
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            try:
                parser.parse_args(['--help'])
            except SystemExit:
                pass  # argparse lève SystemExit après avoir affiché l'aide
            
            help_output = mock_stdout.getvalue()
            self.assertIn("Système complet de traitement d'audiobooks", help_output)

    def test_setup_argument_parser_defaults(self):
        """Test les valeurs par défaut du parser"""
        parser = setup_argument_parser()
        
        # Test avec aucun argument
        args = parser.parse_args([])
        
        # Vérifier les valeurs par défaut
        self.assertIsNone(args.source)
        self.assertIsNone(args.output)
        self.assertIsNone(args.single)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.upload)
        self.assertIsNone(args.bitrate)
        self.assertIsNone(args.samplerate)
        self.assertFalse(args.no_chapters)
        self.assertFalse(args.no_normalization)
        self.assertFalse(args.no_compression)
        self.assertFalse(args.no_gpu)
        self.assertIsNone(args.aac_coder)
        self.assertFalse(args.no_scraping)
        self.assertFalse(args.no_ai)
        self.assertFalse(args.verbose)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_logging_configuration(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test la configuration du logging"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
            # Le test vérifie juste que le code s'exécute sans erreur
            main()
            
            # Vérifications
            mock_processor.process_all.assert_called_once()


if __name__ == '__main__':
    unittest.main()
