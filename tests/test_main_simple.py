"""
Tests unitaires pour core/main.py - Version simplifiée
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import sys
from pathlib import Path
from io import StringIO

from core.main import setup_argument_parser


class TestMainSimplified(unittest.TestCase):
    """Tests simplifiés pour le module main"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        
    def test_setup_argument_parser(self):
        """Test la création du parser d'arguments"""
        parser = setup_argument_parser()
        
        # Vérifie que les options principales existent
        args = parser.parse_args([])
        
        # Test valeurs par défaut
        self.assertIsNone(args.source)
        self.assertIsNone(args.output)
        self.assertIsNone(args.single)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.upload)
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
            '--bitrate', '128k',
            '--verbose'
        ])
        
        self.assertEqual(args.source, '/test/source')
        self.assertEqual(args.output, '/test/output')
        self.assertEqual(args.single, 'test.mp3')
        self.assertTrue(args.dry_run)
        self.assertTrue(args.upload)
        self.assertEqual(args.bitrate, '128k')
        self.assertTrue(args.verbose)
        
    def test_setup_argument_parser_basic_options(self):
        """Test les options de base du parser"""
        parser = setup_argument_parser()
        
        # Vérifie que les options existent
        help_text = parser.format_help()
        
        self.assertIn('--source', help_text)
        self.assertIn('--output', help_text)
        self.assertIn('--single', help_text)
        self.assertIn('--dry-run', help_text)
        self.assertIn('--upload', help_text)
        self.assertIn('--bitrate', help_text)
        self.assertIn('--verbose', help_text)
        
    def test_setup_argument_parser_descriptions(self):
        """Test que les descriptions sont présentes"""
        parser = setup_argument_parser()
        
        help_text = parser.format_help()
        
        self.assertIn('source', help_text.lower())
        self.assertIn('output', help_text.lower())
        self.assertIn('dry', help_text.lower())
        self.assertIn('upload', help_text.lower())
        self.assertIn('bitrate', help_text.lower())
        
    def test_setup_argument_parser_single_file(self):
        """Test l'option single file"""
        parser = setup_argument_parser()
        
        args = parser.parse_args(['--single', 'mon_fichier.mp3'])
        
        self.assertEqual(args.single, 'mon_fichier.mp3')
        self.assertFalse(args.dry_run)
        
    def test_setup_argument_parser_bitrate_validation(self):
        """Test les valeurs de bitrate"""
        parser = setup_argument_parser()
        
        # Test différents bitrates
        test_cases = ['64k', '96k', '128k', '192k']
        
        for bitrate in test_cases:
            args = parser.parse_args(['--bitrate', bitrate])
            self.assertEqual(args.bitrate, bitrate)
            
    def test_setup_argument_parser_boolean_flags(self):
        """Test les flags booléens"""
        parser = setup_argument_parser()
        
        # Test dry-run
        args = parser.parse_args(['--dry-run'])
        self.assertTrue(args.dry_run)
        
        # Test upload
        args = parser.parse_args(['--upload'])
        self.assertTrue(args.upload)
        
        # Test verbose
        args = parser.parse_args(['--verbose'])
        self.assertTrue(args.verbose)
        
    def test_setup_argument_parser_combined(self):
        """Test la combinaison de plusieurs options"""
        parser = setup_argument_parser()
        
        args = parser.parse_args([
            '--source', '/source',
            '--output', '/output',
            '--bitrate', '128k',
            '--dry-run',
            '--verbose'
        ])
        
        self.assertEqual(args.source, '/source')
        self.assertEqual(args.output, '/output')
        self.assertEqual(args.bitrate, '128k')
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)
        self.assertFalse(args.upload)  # Par défaut


if __name__ == '__main__':
    unittest.main()
