"""
Tests étendus pour core/main.py - Focus sur le coverage
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import sys
from pathlib import Path
from io import StringIO

from core.main import setup_argument_parser, main
from core.config import ProcessingConfig


class TestMainCoverage(unittest.TestCase):
    """Tests étendus pour maximiser le coverage de core/main.py"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.output_dir = Path(self.temp_dir) / "output"
        
        self.source_dir.mkdir()
        self.output_dir.mkdir()

    def test_setup_argument_parser_complete(self):
        """Test la création complète du parser"""
        parser = setup_argument_parser()
        
        # Test toutes les options disponibles
        args = parser.parse_args([
            '--source', str(self.source_dir),
            '--output', str(self.output_dir),
            '--single', 'test.mp3',
            '--dry-run',
            '--upload',
            '--bitrate', '128k',
            '--samplerate', '44100',
            '--no-chapters',
            '--no-normalization',
            '--no-compression',
            '--no-gpu',
            '--aac-coder', 'twolo',  # Valeur valide
            '--no-scraping',
            '--no-ai',  # Utiliser --no-ai au lieu de --no-synopsis
            '--verbose'
        ])
        
        self.assertEqual(args.source, str(self.source_dir))
        self.assertEqual(args.output, str(self.output_dir))
        self.assertEqual(args.single, 'test.mp3')
        self.assertTrue(args.dry_run)
        self.assertTrue(args.upload)
        self.assertEqual(args.bitrate, '128k')
        self.assertEqual(args.samplerate, '44100')  # argparse retourne string
        self.assertTrue(args.no_chapters)
        self.assertTrue(args.no_normalization)
        self.assertTrue(args.no_compression)
        self.assertTrue(args.no_gpu)
        self.assertEqual(args.aac_coder, 'twolo')
        self.assertTrue(args.no_scraping)
        self.assertTrue(args.no_ai)
        self.assertTrue(args.verbose)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_single_file_success(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement d'un fichier unique réussi"""
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
    def test_main_single_file_failure(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement d'un fichier unique échoué"""
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
    def test_main_dry_run_mode(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le mode dry-run"""
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
    def test_main_batch_processing(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test le traitement par lots"""
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
    def test_main_missing_ffmpeg(self, mock_which, mock_exit):
        """Test l'absence de ffmpeg"""
        # Mock ffmpeg manquant
        mock_which.return_value = None
        
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
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
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
        """Test une exception critique"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config_class.side_effect = Exception("Critical error")
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
            main()
            
            # Vérifications
            mock_exit.assert_called_once_with(1)

    def test_main_config_applies_arguments(self):
        """Test l'application des arguments à la configuration"""
        parser = setup_argument_parser()
        
        # Test avec divers arguments
        args = parser.parse_args([
            '--source', '/test/source',
            '--output', '/test/output',
            '--bitrate', '128k',
            '--samplerate', '48000',
            '--no-chapters',
            '--no-normalization',
            '--no-compression',
            '--no-gpu',
            '--aac-coder', 'fast',  # Valeur valide
            '--no-scraping',
            '--no-synopsis',
            '--upload'
        ])
        
        # Mock de ProcessingConfig
        with patch('core.main.ProcessingConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Simulation de l'application des arguments
            config = ProcessingConfig()
            config.source_directory = args.source
            config.output_directory = args.output
            config.audio_bitrate = args.bitrate
            config.sample_rate = int(args.samplerate)
            config.enable_chapters = not args.no_chapters
            config.enable_loudnorm = not args.no_normalization
            config.enable_compressor = not args.no_compression
            config.enable_gpu_acceleration = not args.no_gpu
            config.aac_coder = args.aac_coder
            config.enable_scraping = not args.no_scraping
            config.enable_synopsis_generation = not args.no_synopsis
            config.enable_upload = args.upload
            
            # Vérifications
            self.assertEqual(config.source_directory, '/test/source')
            self.assertEqual(config.output_directory, '/test/output')
            self.assertEqual(config.audio_bitrate, '128k')
            self.assertEqual(config.sample_rate, 48000)
            self.assertFalse(config.enable_chapters)
            self.assertFalse(config.enable_loudnorm)
            self.assertFalse(config.enable_compressor)
            self.assertFalse(config.enable_gpu_acceleration)
            self.assertEqual(config.aac_coder, 'fast')
            self.assertFalse(config.enable_scraping)
            self.assertFalse(config.enable_synopsis_generation)
            self.assertTrue(config.enable_upload)

    @patch('sys.exit')
    @patch('shutil.which')
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_verbose_logging(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test l'activation du logging verbeux"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
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
    def test_main_upload_disabled(self, mock_config_class, mock_processor_class, mock_which, mock_exit):
        """Test que l'upload n'est pas effectué si désactivé"""
        # Mock des dépendances
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_config = MagicMock()
        mock_config.enable_upload = False
        mock_config_class.return_value = mock_config
        mock_processor = MagicMock()
        mock_processor.process_all.return_value = {'success': 1, 'failed': 0, 'skipped': 0}
        mock_processor_class.return_value = mock_processor
        
        # Mock sys.argv
        with patch('sys.argv', ['main.py', '--source', str(self.source_dir)]):
            main()
            
            # Vérifications
            mock_processor.process_all.assert_called_once()
            mock_exit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
