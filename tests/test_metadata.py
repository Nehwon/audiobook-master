"""
Tests unitaires pour core/metadata.py
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from core.processor import AudiobookMetadata


class TestAudiobookMetadata(unittest.TestCase):
    """Tests pour la classe AudiobookMetadata"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author",
            series="Test Series",
            series_number="1",
            year="2023",
            genre="Fiction",
            description="A test book description",
            language="fr"
        )
        
    def test_metadata_creation(self):
        """Test la création des métadonnées"""
        self.assertEqual(self.metadata.title, "Test Book")
        self.assertEqual(self.metadata.author, "Test Author")
        self.assertEqual(self.metadata.series, "Test Series")
        self.assertEqual(self.metadata.series_number, "1")
        self.assertEqual(self.metadata.year, "2023")
        self.assertEqual(self.metadata.genre, "Fiction")
        self.assertEqual(self.metadata.language, "fr")
        
    def test_get_filename_format_with_series(self):
        """Test le format de nom de fichier avec série"""
        filename = self.metadata.get_filename_format()
        expected = "Test Author - Test Series - Tome 1 - Test Book"
        self.assertEqual(filename, expected)
        
    def test_get_filename_format_without_series(self):
        """Test le format de nom de fichier sans série"""
        metadata_no_series = AudiobookMetadata(
            title="Simple Book",
            author="Simple Author"
        )
        
        filename = metadata_no_series.get_filename_format()
        expected = "Simple Author - Simple Book"
        self.assertEqual(filename, expected)
        
    def test_get_metadata_dict(self):
        """Test la génération du dictionnaire de métadonnées"""
        metadata_dict = self.metadata.get_metadata_dict()
        
        # Vérifie les champs principaux
        self.assertEqual(metadata_dict['title'], "Test Book")
        self.assertEqual(metadata_dict['artist'], "Test Author")  # narrator = author par défaut
        self.assertEqual(metadata_dict['albumartist'], "Test Author")
        self.assertEqual(metadata_dict['album'], "Test Series")
        self.assertEqual(metadata_dict['genre'], "Fiction")
        self.assertEqual(metadata_dict['date'], "2023")
        self.assertEqual(metadata_dict['language'], "fr")
        
        # Vérifie les champs de série
        self.assertEqual(metadata_dict['series'], "Test Series")
        self.assertEqual(metadata_dict['seriespart'], "1")
        self.assertEqual(metadata_dict['track'], "1")
        
    def test_get_metadata_dict_with_narrator(self):
        """Test les métadonnées avec narrateur"""
        metadata_with_narrator = AudiobookMetadata(
            title="Narrated Book",
            author="Book Author",
            narrator="Voice Actor"
        )
        
        metadata_dict = metadata_with_narrator.get_metadata_dict()
        
        # Vérifie que le narrateur est prioritaire pour artist
        self.assertEqual(metadata_dict['artist'], "Voice Actor")
        self.assertEqual(metadata_dict['albumartist'], "Book Author")
        self.assertEqual(metadata_dict['©narr'], "Voice Actor")
        
    def test_get_metadata_dict_filters_empty_values(self):
        """Test que les valeurs vides sont filtrées"""
        metadata_partial = AudiobookMetadata(
            title="Test",
            author="Author",
            genre="",  # Vide
            year=None  # None
        )
        
        metadata_dict = metadata_partial.get_metadata_dict()
        
        # Vérifie que les champs vides sont absents (sauf ceux avec valeurs par défaut)
        self.assertNotIn('date', metadata_dict)  # year=None
        # genre a une valeur par défaut "Audiobook" dans get_metadata_dict, donc on teste autre chose
        
    def test_get_metadata_dict_with_asin(self):
        """Test les métadonnées avec ASIN"""
        metadata_with_asin = AudiobookMetadata(
            title="Amazon Book",
            author="Amazon Author",
            asin="B123456789"
        )
        
        metadata_dict = metadata_with_asin.get_metadata_dict()
        self.assertEqual(metadata_dict['ASIN'], "B123456789")


if __name__ == '__main__':
    unittest.main()
