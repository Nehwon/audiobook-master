"""
Tests unitaires pour ai/synopsis/generator.py
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import subprocess
from pathlib import Path

from ai.synopsis.generator import SynopsisGenerator, SynopsisConfig


class TestSynopsisGenerator(unittest.TestCase):
    """Tests pour la classe SynopsisGenerator"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.generator = SynopsisGenerator()
        self.title = "Le Seigneur des Anneaux"
        self.author = "J.R.R. Tolkien"
        
    @patch('subprocess.run')
    def test_generate_synopsis_success(self, mock_run):
        """Test la génération réussie d'un synopsis"""
        # Configure le mock pour simuler Ollama
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Un synopsis généré avec succès pour ce livre épique."
        
        # Test la génération
        synopsis = self.generator.generate_synopsis(self.title, self.author)
        
        # Vérifications
        self.assertIsNotNone(synopsis)
        self.assertIn("synopsis généré", synopsis.lower())
        
        # Vérifie que subprocess.run a été appelé avec les bons paramètres
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], 'ollama')
        self.assertEqual(args[1], 'run')
        self.assertIn(self.title, ' '.join(args))
        self.assertIn(self.author, ' '.join(args))
        
    @patch('subprocess.run')
    def test_generate_synopsis_failure(self, mock_run):
        """Test l'échec de la génération de synopsis"""
        # Configure le mock pour simuler un échec
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Ollama error"
        
        # Test la génération
        synopsis = self.generator.generate_synopsis(self.title, self.author)
        
        # Vérifications
        self.assertIsNotNone(synopsis)
        self.assertIn(self.title, synopsis)
        self.assertIn(self.author, synopsis)
        
    @patch('subprocess.run')
    def test_generate_synopsis_timeout(self, mock_run):
        """Test le timeout lors de la génération"""
        # Configure le mock pour simuler un timeout
        mock_run.side_effect = subprocess.TimeoutExpired('ollama', 30)
        
        # Test la génération
        synopsis = self.generator.generate_synopsis(self.title, self.author)
        
        # Vérifications
        self.assertIsNotNone(synopsis)
        self.assertIn(self.title, synopsis)
        
    def test_validate_synopsis_valid(self):
        """Test la validation d'un synopsis valide"""
        valid_synopsis = (
            "Ceci est un synopsis valide pour un livre. "
            "Il contient une introduction intéressante et un développement. "
            "L'histoire est captivante sans révéler la fin."
        )
        
        result = self.generator.validate_synopsis(valid_synopsis)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['word_count'], 30)
        self.assertEqual(result['length_status'], 'valid')
        
    def test_validate_synopsis_too_short(self):
        """Test la validation d'un synopsis trop court"""
        short_synopsis = "Trop court"
        
        result = self.generator.validate_synopsis(short_synopsis)
        
        self.assertFalse(result['valid'])
        self.assertEqual(result['length_status'], 'too_short')
        self.assertIn('trop court', result['error'].lower())
        
    def test_validate_synopsis_too_long(self):
        """Test la validation d'un synopsis trop long"""
        long_synopsis = "word " * 400  # 400 mots
        
        result = self.generator.validate_synopsis(long_synopsis)
        
        self.assertFalse(result['valid'])
        self.assertEqual(result['length_status'], 'too_long')
        self.assertIn('trop long', result['error'].lower())
        
    def test_validate_synopsis_with_spoilers(self):
        """Test la validation d'un synopsis avec spoilers"""
        spoiler_synopsis = (
            "Une histoire intéressante. "
            "Le héros meurt à la fin et tout le monde était un rêve. "
            "C'était un spoiler évident."
        )
        
        result = self.generator.validate_synopsis(spoiler_synopsis)
        
        self.assertFalse(result['valid'])
        self.assertEqual(result['length_status'], 'valid')
        self.assertIn('spoiler', result['error'].lower())
        
    def test_build_prompt_french(self):
        """Test la construction du prompt en français"""
        prompt = self.generator._build_prompt(self.title, self.author)
        
        self.assertIn(self.title, prompt)
        self.assertIn(self.author, prompt)
        self.assertIn("150-300 mots", prompt)
        self.assertIn("sans spoiler", prompt)
        self.assertIn("français", prompt)
        
    def test_build_prompt_english(self):
        """Test la construction du prompt en anglais"""
        config = SynopsisConfig(language="en")
        generator = SynopsisGenerator(config)
        
        prompt = generator._build_prompt(self.title, self.author)
        
        self.assertIn(self.title, prompt)
        self.assertIn(self.author, prompt)
        self.assertIn("150-300 words", prompt)
        self.assertIn("no spoilers", prompt)
        self.assertIn("English", prompt)


if __name__ == '__main__':
    unittest.main()
