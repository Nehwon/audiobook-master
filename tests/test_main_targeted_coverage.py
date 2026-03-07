"""
Tests ciblés pour core/main.py - Focus sur les fonctions manquantes pour atteindre 80%
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path
import sys
import io

from core.main import setup_argument_parser, main
from core.config import ProcessingConfig


class TestMainTargetedCoverage(unittest.TestCase):
    """Tests ciblés pour couvrir les fonctions manquantes de main.py et atteindre 80%"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.output_dir = Path(self.temp_dir) / "output"

        self.source_dir.mkdir()
        self.output_dir.mkdir()

    def test_setup_argument_parser_default_values(self):
        """Test le parser avec valeurs par défaut"""
        parser = setup_argument_parser()
        
        args = parser.parse_args(['--source', str(self.source_dir)])
        
        self.assertEqual(args.source, str(self.source_dir))
        self.assertIsNone(args.output)
        self.assertIsNone(args.single)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.upload)
        self.assertIsNone(args.bitrate)  # None par défaut
        self.assertIsNone(args.samplerate)  # None par défaut
        self.assertFalse(args.no_chapters)
        self.assertFalse(args.no_normalization)
        self.assertFalse(args.no_compression)
        self.assertFalse(args.no_gpu)
        self.assertIsNone(args.aac_coder)  # None par défaut
        self.assertFalse(args.no_scraping)
        self.assertFalse(args.no_ai)
        self.assertFalse(args.verbose)

    def test_setup_argument_parser_bitrate_validation(self):
        """Test la configuration du bitrate"""
        parser = setup_argument_parser()
        
        # Test bitrate valide
        args = parser.parse_args(['--source', str(self.source_dir), '--bitrate', '256k'])
        self.assertEqual(args.bitrate, '256k')

    def test_setup_argument_parser_samplerate_validation(self):
        """Test la configuration du sample rate"""
        parser = setup_argument_parser()
        
        # Test sample rate valide
        args = parser.parse_args(['--source', str(self.source_dir), '--samplerate', '48000'])
        self.assertEqual(args.samplerate, 48000)  # argparse retourne int

    def test_setup_argument_parser_aac_coder_validation(self):
        """Test la validation du AAC coder"""
        parser = setup_argument_parser()
        
        # Test AAC coder valide
        args = parser.parse_args(['--source', str(self.source_dir), '--aac-coder', 'twolo'])
        self.assertEqual(args.aac_coder, 'twolo')
        
        # Test AAC coder invalide
        with self.assertRaises(SystemExit):
            parser.parse_args(['--source', str(self.source_dir), '--aac-coder', 'invalid'])

    def test_setup_argument_parser_source_required(self):
        """Test que source reste optionnel pour compatibilité CLI actuelle"""
        parser = setup_argument_parser()
        
        args = parser.parse_args([])
        self.assertIsNone(args.source)

    def test_setup_argument_parser_output_directory(self):
        """Test la configuration du répertoire de sortie"""
        parser = setup_argument_parser()
        
        args = parser.parse_args([
            '--source', str(self.source_dir),
            '--output', str(self.output_dir)
        ])
        
        self.assertEqual(args.output, str(self.output_dir))

    def test_setup_argument_parser_single_file(self):
        """Test la configuration de fichier unique"""
        parser = setup_argument_parser()
        
        args = parser.parse_args([
            '--source', str(self.source_dir),
            '--single', 'test.mp3'
        ])
        
        self.assertEqual(args.single, 'test.mp3')

    def test_setup_argument_parser_boolean_flags(self):
        """Test tous les flags booléens"""
        parser = setup_argument_parser()
        
        args = parser.parse_args([
            '--source', str(self.source_dir),
            '--dry-run',
            '--upload',
            '--no-chapters',
            '--no-normalization',
            '--no-compression',
            '--no-gpu',
            '--no-scraping',
            '--no-ai',
            '--verbose'
        ])
        
        self.assertTrue(args.dry_run)
        self.assertTrue(args.upload)
        self.assertTrue(args.no_chapters)
        self.assertTrue(args.no_normalization)
        self.assertTrue(args.no_compression)
        self.assertTrue(args.no_gpu)
        self.assertTrue(args.no_scraping)
        self.assertTrue(args.no_ai)
        self.assertTrue(args.verbose)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_single_file_dry_run(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le mode dry-run avec fichier unique"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.parse_filename.return_value = MagicMock(title="Test", author="Author")
        mock_processor_class.return_value = mock_processor
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--single', 'test.mp3', '--dry-run']):
            main()
            
            # Vérifications
            mock_processor.parse_filename.assert_called_once()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_batch_processing_success(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement par lot réussi"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 2, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
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
    def test_main_batch_processing_with_failures(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement par lot avec des échecs (pas d'exit dur)"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 1, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
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
    def test_main_single_file_processing_success(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement de fichier unique réussi"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_audiobook.return_value = True
        mock_processor_class.return_value = mock_processor
        
        # Créer un fichier test
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio content")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--single', 'test.mp3']):
            main()
            
            # Vérifications
            mock_processor.process_audiobook.assert_called_once()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_single_file_processing_failure(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement de fichier unique avec échec"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_audiobook.return_value = False
        mock_processor_class.return_value = mock_processor
        
        # Créer un fichier test
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio content")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--single', 'test.mp3']):
            main()
            
            # Vérifications
            mock_processor.process_audiobook.assert_called_once()
            mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_verbose_logging(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le mode verbose"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 0, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # Mock sys.argv et logger
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--verbose']):
            with patch('core.main.logging.getLogger') as mock_logger:
                mock_logger_instance = MagicMock()
                mock_logger.return_value = mock_logger_instance
                
                main()
                
                # Vérifications
                mock_logger_instance.setLevel.assert_called_once()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_custom_output_directory(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test avec répertoire de sortie personnalisé"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--output', str(self.output_dir)]):
            main()
            
            # Vérifications
            mock_processor.process_all.assert_called_once()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    @patch('core.main.AudiobookshelfClient')
    def test_main_upload_enabled(self, mock_abs_client_class, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test avec upload activé"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config.enable_upload = True
        mock_config.audiobookshelf_host = "http://localhost:13378"
        mock_config.audiobookshelf_user = "admin"
        mock_config.audiobookshelf_password = "password"
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
    def test_main_missing_ffmpeg(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test l'absence de ffmpeg"""
        # Mock des dépendances
        mock_which.return_value = None  # ffmpeg non trouvé
        mock_config_class.return_value = MagicMock()
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
            main()
            
            # Vérifications
            mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_missing_ollama(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test l'absence d'ollama quand synopsis activé"""
        # Mock des dépendances
        def mock_which_func(cmd):
            if cmd == 'ffmpeg':
                return '/usr/bin/ffmpeg'
            elif cmd == 'ollama':
                return None
            return None
        
        mock_which.side_effect = mock_which_func
        mock_config = MagicMock()
        mock_config.enable_synopsis_generation = True
        mock_config_class.return_value = mock_config
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
            main()
            
            # Vérifications
            mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_file_not_found(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le fichier non trouvé"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config_class.return_value = MagicMock()
        
        # Mock sys.argv avec fichier inexistant
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--single', 'nonexistent.mp3']):
            main()
            
            # Vérifications
            mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_critical_exception(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test la gestion des exceptions critiques"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config_class.side_effect = Exception("Critical error")
        
        # Mock sys.argv
        try:
            with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
                main()
        except Exception:
            pass  # L'exception est gérée
        
        # Vérifications
        mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
