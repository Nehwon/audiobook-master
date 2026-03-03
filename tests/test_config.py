"""
Tests unitaires pour core/config.py
"""

import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path

from core.config import ProcessingConfig


class TestProcessingConfig(unittest.TestCase):
    """Tests pour la classe ProcessingConfig"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        
    def test_default_config(self):
        """Test la configuration par défaut"""
        config = ProcessingConfig()
        
        # Vérifie les valeurs par défaut
        self.assertEqual(config.audio_bitrate, "192k")
        self.assertEqual(config.audio_channels, 2)
        self.assertEqual(config.sample_rate, 44100)
        self.assertTrue(config.enable_gpu_acceleration)
        self.assertTrue(config.enable_loudnorm)
        self.assertTrue(config.enable_scraping)
        self.assertFalse(config.enable_upload)
        
    def test_custom_config(self):
        """Test la configuration personnalisée"""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        config = ProcessingConfig(
            source_directory=temp_dir + "/source",
            output_directory=temp_dir + "/output",
            audio_bitrate="128k",
            enable_gpu_acceleration=False
        )
        
        self.assertEqual(config.source_directory, temp_dir + "/source")
        self.assertEqual(config.output_directory, temp_dir + "/output")
        self.assertEqual(config.audio_bitrate, "128k")
        self.assertFalse(config.enable_gpu_acceleration)
        
    def test_post_init_creates_directories(self):
        """Test que __post_init__ crée les répertoires"""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        config = ProcessingConfig(
            source_directory=temp_dir + "/source",
            output_directory=temp_dir + "/output",
            temp_directory=temp_dir + "/temp"
        )
        
        # Vérifie que les répertoires ont été créés
        self.assertTrue(Path(config.source_directory).exists())
        self.assertTrue(Path(config.output_directory).exists())
        self.assertTrue(Path(config.temp_directory).exists())
        
    def test_scraping_sources_default(self):
        """Test les sources de scraping par défaut"""
        config = ProcessingConfig()
        
        self.assertIsNotNone(config.scraping_sources)
        self.assertIn("babelio", config.scraping_sources)
        self.assertIn("fnac", config.scraping_sources)
        
    def test_scraping_sources_custom(self):
        """Test les sources de scraping personnalisées"""
        custom_sources = ["custom1", "custom2"]
        config = ProcessingConfig(scraping_sources=custom_sources)
        
        self.assertEqual(config.scraping_sources, custom_sources)


if __name__ == '__main__':
    unittest.main()
