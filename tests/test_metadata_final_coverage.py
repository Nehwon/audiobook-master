"""
Tests étendus pour core/metadata.py - Focus sur le coverage des fonctions manquantes pour atteindre 60%
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
from pathlib import Path

from core.metadata import BookInfo, AudibleScraper, BabelioScraper


class TestMetadataFinalCoverage(unittest.TestCase):
    """Tests étendus pour couvrir les fonctions manquantes de metadata.py et atteindre 60%"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()

    def test_audible_scraper_search_with_pagination(self):
        """Test la recherche Audible avec pagination"""
        scraper = AudibleScraper()
        
        with patch('requests.Session.get') as mock_get:
            # Mock de la première page
            mock_response1 = MagicMock()
            mock_response1.raise_for_status.return_value = None
            mock_response1.content = b'<html><div class="productListItem">Book 1</div><a class="nextLink">Next</a></html>'
            
            # Mock de la deuxième page
            mock_response2 = MagicMock()
            mock_response2.raise_for_status.return_value = None
            mock_response2.content = b'<html><div class="productListItem">Book 2</div></html>'
            
            mock_get.side_effect = [mock_response1, mock_response2]
            
            # Mock du parsing pour retourner un résultat
            with patch.object(scraper, '_parse_audible_results') as mock_parse:
                mock_parse.return_value = BookInfo(title="Test Book", author="Test Author")
                
                result = scraper.search_audible("Test Author", "Test Book")
                
                self.assertIsNotNone(result)
                self.assertEqual(mock_get.call_count, 2)

    def test_audible_scraper_search_with_special_characters(self):
        """Test la recherche Audible avec caractères spéciaux"""
        scraper = AudibleScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><div class="productListItem">Book</div></html>'
            mock_get.return_value = mock_response
            
            result = scraper.search_audible("Test Author & Co", "Test Book: Special Edition")
            
            # Vérifie que la recherche gère les caractères spéciaux
            mock_get.assert_called_once()
            self.assertIsNone(result)  # Pas de résultats parsés

    def test_audible_scraper_search_with_language_filter(self):
        """Test la recherche Audible avec filtre de langue"""
        scraper = AudibleScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><div class="productListItem">Book</div></html>'
            mock_get.return_value = mock_response
            
            with patch.object(scraper, '_parse_audible_results') as mock_parse:
                mock_parse.return_value = BookInfo(title="Test Book", author="Test Author")
                
                result = scraper.search_audible("Test Author", "Test Book", language="fr")
                
                self.assertIsNotNone(result)
                mock_get.assert_called_once()

    def test_audible_scraper_extract_rating_with_decimal(self):
        """Test l'extraction de note avec décimales"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_rating = MagicMock()
        mock_rating.get_text.return_value = "4.5 out of 5 stars"
        mock_book.select_one.return_value = mock_rating
        
        result = scraper._extract_audible_rating(mock_book)
        
        self.assertEqual(result, 4.5)

    def test_audible_scraper_extract_rating_no_rating(self):
        """Test l'extraction sans note"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_book.select_one.return_value = None
        
        result = scraper._extract_audible_rating(mock_book)
        
        self.assertIsNone(result)

    def test_audible_scraper_extract_narrator_with_prefix(self):
        """Test l'extraction du narrateur avec préfixe"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_narrator = MagicMock()
        mock_narrator.get_text.return_value = "Narrated by: Test Narrator"
        mock_book.select_one.return_value = mock_narrator
        
        result = scraper._extract_audible_narrator(mock_book)
        
        self.assertEqual(result, "Narrated by: Test Narrator")

    def test_audible_scraper_extract_length_with_hours_and_minutes(self):
        """Test l'extraction de durée avec heures et minutes"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_length = MagicMock()
        mock_length.get_text.return_value = "Length: 12 hr 30 min"
        mock_book.select_one.return_value = mock_length
        
        result = scraper._extract_audible_length(mock_book)
        
        self.assertEqual(result, "12 hr 30 min")

    def test_audible_scraper_extract_length_only_minutes(self):
        """Test l'extraction de durée avec seulement des minutes"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_length = MagicMock()
        mock_length.get_text.return_value = "Length: 45 min"
        mock_book.select_one.return_value = mock_length
        
        result = scraper._extract_audible_length(mock_book)
        
        self.assertEqual(result, "45 min")

    def test_babelio_scraper_search_with_pagination(self):
        """Test la recherche Babelio avec pagination"""
        scraper = BabelioScraper()
        
        with patch('requests.Session.get') as mock_get:
            # Mock de la première page
            mock_response1 = MagicMock()
            mock_response1.raise_for_status.return_value = None
            mock_response1.content = b'<html><div class="list_livre">Book 1</div><a class="next">Next</a></html>'
            
            # Mock de la deuxième page
            mock_response2 = MagicMock()
            mock_response2.raise_for_status.return_value = None
            mock_response2.content = b'<html><div class="list_livre">Book 2</div></html>'
            
            mock_get.side_effect = [mock_response1, mock_response2]
            
            with patch.object(scraper, '_parse_search_results') as mock_parse:
                mock_parse.return_value = BookInfo(title="Test Book", author="Test Author")
                
                result = scraper.search_babelio("Test Author", "Test Book")
                
                self.assertIsNotNone(result)
                self.assertEqual(mock_get.call_count, 2)

    def test_babelio_scraper_search_with_special_characters(self):
        """Test la recherche Babelio avec caractères spéciaux"""
        scraper = BabelioScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><div class="list_livre">Book</div></html>'
            mock_get.return_value = mock_response
            
            result = scraper.search_babelio("Test Author & Co", "Test Book: Special Edition")
            
            # Vérifie que la recherche gère les caractères spéciaux
            mock_get.assert_called_once()
            self.assertIsNone(result)  # Pas de résultats parsés

    def test_babelio_scraper_download_cover_with_subdirectory(self):
        """Test le téléchargement de pochette avec sous-répertoire"""
        scraper = BabelioScraper()
        cover_url = "http://example.com/cover.jpg"
        save_path = Path(self.temp_dir) / "subdir" / "cover.jpg"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b"fake image content"
            mock_get.return_value = mock_response
            
            result = scraper.download_cover(cover_url, save_path)
            
            self.assertTrue(result)
            self.assertTrue(save_path.exists())

    def test_babelio_scraper_download_cover_invalid_url(self):
        """Test le téléchargement avec URL invalide"""
        scraper = BabelioScraper()
        cover_url = "invalid-url"
        save_path = Path(self.temp_dir) / "cover.jpg"
        
        result = scraper.download_cover(cover_url, save_path)
        
        self.assertFalse(result)

    def test_babelio_scraper_download_cover_permission_error(self):
        """Test le téléchargement avec erreur de permissions"""
        scraper = BabelioScraper()
        cover_url = "http://example.com/cover.jpg"
        save_path = Path("/root/cover.jpg")  # Chemin inaccessible
        
        result = scraper.download_cover(cover_url, save_path)
        
        self.assertFalse(result)

    def test_book_info_creation_with_all_fields(self):
        """Test la création de BookInfo avec tous les champs"""
        book_info = BookInfo(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            publication_date="2023",
            isbn="1234567890",
            pages=300,
            language="fr",
            description="Test description",
            cover_url="http://example.com/cover.jpg",
            rating=4.5,
            genres=["Fiction", "Thriller"],
            series="Test Series",
            series_number="1",
            duration="10h30m",
            asin="B123456789"
        )
        
        self.assertEqual(book_info.title, "Test Book")
        self.assertEqual(book_info.author, "Test Author")
        self.assertEqual(book_info.publisher, "Test Publisher")
        self.assertEqual(book_info.publication_date, "2023")
        self.assertEqual(book_info.isbn, "1234567890")
        self.assertEqual(book_info.pages, 300)
        self.assertEqual(book_info.language, "fr")
        self.assertEqual(book_info.description, "Test description")
        self.assertEqual(book_info.cover_url, "http://example.com/cover.jpg")
        self.assertEqual(book_info.rating, 4.5)
        self.assertEqual(book_info.genres, ["Fiction", "Thriller"])
        self.assertEqual(book_info.series, "Test Series")
        self.assertEqual(book_info.series_number, "1")
        self.assertEqual(book_info.duration, "10h30m")
        self.assertEqual(book_info.asin, "B123456789")

    def test_book_info_creation_with_minimal_fields(self):
        """Test la création de BookInfo avec champs minimaux"""
        book_info = BookInfo(title="Test", author="Author")
        
        self.assertEqual(book_info.title, "Test")
        self.assertEqual(book_info.author, "Author")
        self.assertIsNone(book_info.publisher)
        self.assertIsNone(book_info.publication_date)
        self.assertIsNone(book_info.isbn)
        self.assertIsNone(book_info.pages)
        self.assertEqual(book_info.language, "fr")  # Valeur par défaut
        self.assertIsNone(book_info.description)
        self.assertIsNone(book_info.cover_url)
        self.assertIsNone(book_info.rating)
        self.assertEqual(book_info.genres, [])
        self.assertIsNone(book_info.series)
        self.assertIsNone(book_info.series_number)
        self.assertIsNone(book_info.duration)
        self.assertIsNone(book_info.asin)

    def test_book_info_str_with_series(self):
        """Test la représentation string avec série"""
        book_info = BookInfo(
            title="Test Book",
            author="Test Author",
            series="Test Series",
            series_number="1"
        )
        
        result = str(book_info)
        
        self.assertIn("Test Book", result)
        self.assertIn("Test Author", result)
        self.assertIn("Test Series", result)
        self.assertIn("1", result)

    def test_book_info_str_without_series(self):
        """Test la représentation string sans série"""
        book_info = BookInfo(title="Test Book", author="Test Author")
        
        result = str(book_info)
        
        self.assertIn("Test Book", result)
        self.assertIn("Test Author", result)
        self.assertNotIn("Series", result)

    def test_book_info_str_with_long_title(self):
        """Test la représentation string avec titre long"""
        book_info = BookInfo(
            title="This is a very long title that might need to be truncated",
            author="Test Author"
        )
        
        result = str(book_info)
        
        self.assertIn("This is a very long title", result)
        self.assertIn("Test Author", result)

    def test_audible_similarity_calculation_identical_strings(self):
        """Test le calcul de similarité avec chaînes identiques"""
        scraper = AudibleScraper()
        
        similarity = scraper._calculate_similarity("test", "test")
        
        self.assertEqual(similarity, 1.0)

    def test_audible_similarity_calculation_different_strings(self):
        """Test le calcul de similarité avec chaînes différentes"""
        scraper = AudibleScraper()
        
        similarity = scraper._calculate_similarity("test", "other")
        
        self.assertEqual(similarity, 0.0)

    def test_audible_similarity_calculation_partial_match(self):
        """Test le calcul de similarité avec correspondance partielle"""
        scraper = AudibleScraper()
        
        similarity = scraper._calculate_similarity("test word", "test other")
        
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)

    def test_audible_similarity_calculation_empty_strings(self):
        """Test le calcul de similarité avec chaînes vides"""
        scraper = AudibleScraper()
        
        similarity = scraper._calculate_similarity("", "")
        
        self.assertEqual(similarity, 1.0)

    def test_audible_similarity_calculation_one_empty_string(self):
        """Test le calcul de similarité avec une chaîne vide"""
        scraper = AudibleScraper()
        
        similarity = scraper._calculate_similarity("test", "")
        
        self.assertEqual(similarity, 0.0)

    def test_audible_match_validation_perfect_match(self):
        """Test la validation de correspondance parfaite"""
        scraper = AudibleScraper()
        
        result = scraper._is_match("Test Book", "Test Author", "Test Book", "Test Author")
        
        self.assertTrue(result)

    def test_audible_match_validation_no_match(self):
        """Test la validation sans correspondance"""
        scraper = AudibleScraper()
        
        result = scraper._is_match("Test Book", "Test Author", "Other Book", "Other Author")
        
        self.assertFalse(result)

    def test_audible_match_validation_partial_match(self):
        """Test la validation avec correspondance partielle"""
        scraper = AudibleScraper()
        
        result = scraper._is_match("Test Book", "Test Author", "Test Book", "Other Author")
        
        self.assertFalse(result)  # Nécessite correspondance parfaite

    def test_audible_match_validation_case_insensitive(self):
        """Test la validation insensible à la casse"""
        scraper = AudibleScraper()
        
        result = scraper._is_match("test book", "test author", "TEST BOOK", "TEST AUTHOR")
        
        self.assertTrue(result)

    def test_audible_match_validation_with_extra_spaces(self):
        """Test la validation avec espaces supplémentaires"""
        scraper = AudibleScraper()
        
        result = scraper._is_match("Test Book", "Test Author", "  Test Book  ", "  Test Author  ")
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
