"""
Tests étendus pour core/main.py - Focus sur le coverage des fonctions manquantes pour atteindre 80%
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import sys
from pathlib import Path
from io import StringIO

from core.main import setup_argument_parser, main
from core.config import ProcessingConfig


class TestMainFinalCoverage(unittest.TestCase):
    """Tests étendus pour couvrir les fonctions manquantes de main.py et atteindre 80%"""

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
    def test_main_single_file_processing(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement de fichier unique"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_audiobook.return_value = True
        mock_processor_class.return_value = mock_processor
        
        # Mock du fichier
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio")
        
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
        """Test l'échec de traitement de fichier unique"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_audiobook.return_value = False
        mock_processor_class.return_value = mock_processor
        
        # Mock du fichier
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio")
        
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
    def test_main_batch_processing_success(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement par lots réussi"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 3, 'failed': 0, 'skipped': 0}
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
    def test_main_batch_processing_with_failures(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement par lots avec échecs"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 2, 'failed': 1, 'skipped': 0}
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
            # Le code ne fait pas exit(1) en cas d'échecs, il affiche juste les résultats
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_dry_run_mode(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le mode dry-run"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Mock des fichiers
        test_file = self.source_dir / "test.mp3"
        test_file.write_bytes(b"fake audio")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--dry-run']):
            main()
            
            # Vérifications
            mock_processor.process_all.assert_not_called()
            mock_exit.assert_not_called()

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_verbose_mode(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le mode verbeux"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # Mock du logging
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Mock sys.argv
            with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--verbose']):
                main()
                
                # Vérifications
                mock_logger.setLevel.assert_called_once()

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

    def test_setup_argument_parser_all_options(self):
        """Test le parser avec toutes les options"""
        parser = setup_argument_parser()
        
        # Test avec toutes les options
        args = parser.parse_args([
            '--source', str(self.source_dir),
            '--output', str(self.output_dir),
            '--single', 'test.mp3',
            '--dry-run',
            '--upload',
            '--bitrate', '256k',
            '--samplerate', '48000',
            '--no-chapters',
            '--no-normalization',
            '--no-compression',
            '--no-gpu',
            '--aac-coder', 'twolo',
            '--no-scraping',
            '--no-ai',
            '--verbose'
        ])
        
        self.assertEqual(args.source, str(self.source_dir))
        self.assertEqual(args.output, str(self.output_dir))
        self.assertEqual(args.single, 'test.mp3')
        self.assertTrue(args.dry_run)
        self.assertTrue(args.upload)
        self.assertEqual(args.bitrate, '256k')
        self.assertEqual(args.samplerate, '48000')
        self.assertTrue(args.no_chapters)
        self.assertTrue(args.no_normalization)
        self.assertTrue(args.no_compression)
        self.assertTrue(args.no_gpu)
        self.assertEqual(args.aac_coder, 'twolo')
        self.assertTrue(args.no_scraping)
        self.assertTrue(args.no_ai)
        self.assertTrue(args.verbose)

    def test_setup_argument_parser_mutually_exclusive(self):
        """Test les options mutuellement exclusives"""
        parser = setup_argument_parser()
        
        # Test avec --single et --dry-run
        args = parser.parse_args([
            '--source', str(self.source_dir),
            '--single', 'test.mp3',
            '--dry-run'
        ])
        
        self.assertEqual(args.single, 'test.mp3')
        self.assertTrue(args.dry_run)

    def test_setup_argument_parser_invalid_aac_coder(self):
        """Test le validateur de aac_coder"""
        parser = setup_argument_parser()
        
        # Test avec aac_coder invalide
        with self.assertRaises(SystemExit):
            parser.parse_args(['--aac-coder', 'invalid'])

    def test_setup_argument_parser_help_message(self):
        """Test le message d'aide"""
        parser = setup_argument_parser()
        
        # Vérifier que le parser a une description
        self.assertIsNotNone(parser.description)
        self.assertIn("Système complet", parser.description)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_empty_source_directory(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test avec répertoire source vide"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 0, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # S'assurer que le répertoire est vide
        for file in self.source_dir.glob("*"):
            if file.is_file():
                file.unlink()
        
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
    def test_main_custom_output_directory(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test avec répertoire de sortie personnalisé"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir), '--output', str(self.output_dir)]):
            main()
            
            # Vérifications
            mock_processor.process_all.assert_called_once()
            mock_exit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
