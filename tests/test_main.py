"""
Tests unitaires pour core/main.py
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import sys
from pathlib import Path
from io import StringIO

from core.main import setup_argument_parser, main


class TestMain(unittest.TestCase):
    """Tests pour le module main"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        
    def test_setup_argument_parser(self):
        """Test la création du parser d'arguments"""
        parser = setup_argument_parser()
        
        # Vérifie que les options principales existent
        self.assertTrue(parser.has_option('--source'))
        self.assertTrue(parser.has_option('--output'))
        self.assertTrue(parser.has_option('--single'))
        self.assertTrue(parser.has_option('--dry-run'))
        self.assertTrue(parser.has_option('--upload'))
        self.assertTrue(parser.has_option('--abs-token'))
        self.assertTrue(parser.has_option('--abs-library-id'))
        self.assertTrue(parser.has_option('--bitrate'))
        self.assertTrue(parser.has_option('--verbose'))
        
    def test_setup_argument_parser_defaults(self):
        """Test les valeurs par défaut du parser"""
        parser = setup_argument_parser()
        
        # Test avec aucun argument
        args = parser.parse_args([])
        
        self.assertIsNone(args.source)
        self.assertIsNone(args.output)
        self.assertIsNone(args.single)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.upload)
        self.assertIsNone(args.abs_token)
        self.assertIsNone(args.abs_library_id)
        self.assertIsNone(args.bitrate)
        self.assertFalse(args.verbose)
        
    def test_setup_argument_parser_values(self):
        """Test les valeurs personnalisées du parser"""
        parser = setup_argument_parser()
        
        # Test avec arguments personnalisés
        args = parser.parse_args([
            '--source', '/test/source',
            '--output', '/test/output',
            '--single', 'test.mp3',
            '--dry-run',
            '--upload',
            '--abs-token', 'token-123',
            '--abs-library-id', 'lib-main',
            '--bitrate', '128k',
            '--verbose'
        ])
        
        self.assertEqual(args.source, '/test/source')
        self.assertEqual(args.output, '/test/output')
        self.assertEqual(args.single, 'test.mp3')
        self.assertTrue(args.dry_run)
        self.assertTrue(args.upload)
        self.assertEqual(args.abs_token, 'token-123')
        self.assertEqual(args.abs_library_id, 'lib-main')
        self.assertEqual(args.bitrate, '128k')
        self.assertTrue(args.verbose)
        
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    @patch('core.main.pathlib.Path.exists')
    def test_main_single_file_success(self, mock_exists, mock_config, mock_processor):
        """Test le traitement d'un seul fichier avec succès"""
        # Configuration des mocks
        mock_exists.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        mock_processor_instance.process_audiobook.return_value = True
        
        # Simulation des arguments
        test_args = ['main.py', '--single', 'test.mp3']
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.logger') as mock_logger:
                main()
                
                # Vérifications
                mock_processor.assert_called_once()
                mock_processor_instance.process_audiobook.assert_called_once()
                mock_logger.info.assert_called()
                
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    @patch('core.main.pathlib.Path.exists')
    def test_main_single_file_failure(self, mock_exists, mock_config, mock_processor):
        """Test le traitement d'un seul fichier avec échec"""
        # Configuration des mocks
        mock_exists.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        mock_processor_instance.process_audiobook.return_value = False
        
        # Simulation des arguments
        test_args = ['main.py', '--single', 'test.mp3']
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.logger') as mock_logger:
                with patch('sys.exit') as mock_exit:
                    main()
                    
                    # Vérifications
                    mock_exit.assert_called_once_with(1)
                    mock_logger.error.assert_called()
                    
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_dry_run_mode(self, mock_config, mock_processor):
        """Test le mode simulation (dry-run)"""
        # Configuration des mocks
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        
        # Simulation des arguments
        test_args = ['main.py', '--single', 'test.mp3', '--dry-run']
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.logger') as mock_logger:
                main()
                
                # Vérifications
                mock_processor_instance.parse_filename.assert_called_once()
                mock_logger.info.assert_called()
                # Vérifie que process_audiobook n'est PAS appelé en dry-run
                mock_processor_instance.process_audiobook.assert_not_called()
                
    @patch('core.main.AudiobookProcessor')
    @patch('core.main.ProcessingConfig')
    def test_main_batch_processing(self, mock_config, mock_processor):
        """Test le traitement par lots"""
        # Configuration des mocks
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        mock_processor_instance.process_all.return_value = {
            'success': 5,
            'failed': 1,
            'skipped': 2
        }
        
        # Simulation des arguments
        test_args = ['main.py']
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.logger') as mock_logger:
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Vérifications
                    mock_processor_instance.process_all.assert_called_once()
                    mock_print.assert_called()
                    
    @patch('core.main.ProcessingConfig')
    def test_main_missing_dependencies(self, mock_config):
        """Test la gestion des dépendances manquantes"""
        # Simulation des arguments
        test_args = ['main.py', '--single', 'test.mp3']
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.logger') as mock_logger:
                with patch('core.main.sys.exit') as mock_exit:
                    # Mock ImportError pour les dépendances
                    real_import = __import__

                    def selective_import(name, globals=None, locals=None, fromlist=(), level=0):
                        if name in {'requests', 'bs4', 'PIL', 'mutagen'}:
                            raise ImportError('No module')
                        return real_import(name, globals, locals, fromlist, level)

                    with patch('builtins.__import__', side_effect=selective_import):
                        main()
                        
                        # Vérifications
                        mock_exit.assert_called_once_with(1)
                        mock_logger.error.assert_called()
                        
    @patch('core.main.ProcessingConfig')
    @patch('core.main.shutil.which')
    def test_main_missing_ffmpeg(self, mock_which, mock_config):
        """Test la gestion de FFmpeg manquant"""
        # Configuration des mocks
        mock_which.return_value = None
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        
        # Simulation des arguments
        test_args = ['main.py', '--single', 'test.mp3']
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.logger') as mock_logger:
                with patch('sys.exit') as mock_exit:
                    main()
                    
                    # Vérifications
                    mock_exit.assert_called_once_with(1)
                    mock_logger.error.assert_called_with("ffmpeg n'est pas installé")
                    
    @patch('core.main.ProcessingConfig')
    @patch('core.main.shutil.which')
    def test_main_missing_ollama(self, mock_which, mock_config):
        """Test la gestion d'Ollama manquant"""
        # Configuration des mocks
        mock_which.side_effect = lambda cmd: 'ffmpeg' if cmd == 'ffmpeg' else None
        mock_config_instance = MagicMock()
        mock_config_instance.enable_synopsis_generation = True
        mock_config.return_value = mock_config_instance
        
        # Simulation des arguments
        test_args = ['main.py', '--single', 'test.mp3']
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.logger') as mock_logger:
                with patch('sys.exit') as mock_exit:
                    main()
                    
                    # Vérifications
                    mock_exit.assert_called_once_with(1)
                    mock_logger.error.assert_called_with("Ollama n'est pas installé")
                    
    def test_main_config_applies_arguments(self):
        """Test que la configuration applique correctement les arguments"""
        # Simulation des arguments avec options personnalisées
        test_args = [
            'main.py', 
            '--source', '/custom/source',
            '--output', '/custom/output',
            '--bitrate', '128k',
            '--samplerate', '22050',
            '--no-chapters',
            '--no-normalization',
            '--no-compression',
            '--no-gpu',
            '--aac-coder', 'fast'
        ]
        
        with patch.object(sys, 'argv', test_args):
            with patch('core.main.AudiobookProcessor') as mock_processor:
                with patch('core.main.ProcessingConfig') as mock_config:
                    with patch('core.main.pathlib.Path.exists', return_value=True):
                        with patch('core.main.logger'):
                            main()
                            
                            # Vérifie que la configuration a été modifiée
                            mock_config_instance = mock_config.return_value
                            self.assertEqual(mock_config_instance.source_directory, '/custom/source')
                            self.assertEqual(mock_config_instance.output_directory, '/custom/output')
                            self.assertEqual(mock_config_instance.audio_bitrate, '128k')
                            self.assertEqual(mock_config_instance.sample_rate, 22050)
                            self.assertFalse(mock_config_instance.enable_chapters)
                            self.assertFalse(mock_config_instance.enable_loudnorm)
                            self.assertFalse(mock_config_instance.enable_compressor)
                            self.assertFalse(mock_config_instance.enable_gpu_acceleration)
                            self.assertEqual(mock_config_instance.aac_coder, 'fast')


if __name__ == '__main__':
    unittest.main()
