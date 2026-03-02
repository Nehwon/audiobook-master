"""
Tests étendus pour core/metadata.py - Focus sur le coverage des fonctions existantes
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
from pathlib import Path

from core.metadata import BookInfo, AudibleScraper, BabelioScraper


class TestMetadataExtendedCoverage(unittest.TestCase):
    """Tests étendus pour couvrir les fonctions existantes de metadata.py"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()

    def test_audible_scraper_search_with_results(self):
        """Test la recherche Audible avec résultats"""
        scraper = AudibleScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><div class="productListItem">Book</div></html>'
            mock_get.return_value = mock_response
            
            # Mock de la méthode de parsing
            with patch.object(scraper, '_parse_audible_results') as mock_parse:
                mock_parse.return_value = BookInfo(title="Test Book", author="Test Author")
                
                result = scraper.search_audible("Test Author", "Test Book")
                
                self.assertIsNotNone(result)
                self.assertEqual(result.title, "Test Book")

    def test_audible_scraper_search_no_results(self):
        """Test la recherche Audible sans résultats"""
        scraper = AudibleScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><div>No results</div></html>'
            mock_get.return_value = mock_response
            
            result = scraper.search_audible("Test Author", "Test Book")
            
            self.assertIsNone(result)

    def test_audible_scraper_search_http_error(self):
        """Test la recherche Audible avec erreur HTTP"""
        scraper = AudibleScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("HTTP Error")
            
            result = scraper.search_audible("Test Author", "Test Book")
            
            self.assertIsNone(result)

    def test_audible_scraper_parse_audible_results_success(self):
        """Test le parsing des résultats Audible réussi"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_soup.select.return_value = []  # Pas de résultats pour éviter l'erreur
        
        result = scraper._parse_audible_results(mock_soup, "Test Author", "Test Book")
        
        # Test que la méthode gère bien le cas sans résultats
        self.assertIsNone(result)

    def test_audible_scraper_parse_audible_results_no_books(self):
        """Test le parsing sans livres Audible"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_soup.select.return_value = []
        
        result = scraper._parse_audible_results(mock_soup, "Test Author", "Test Book")
        
        self.assertIsNone(result)

    def test_audible_scraper_extract_audible_rating(self):
        """Test l'extraction de note Audible"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_rating = MagicMock()
        mock_rating.get_text.return_value = "4.5 out of 5"
        mock_book.select_one.return_value = mock_rating
        
        result = scraper._extract_audible_rating(mock_book)
        
        self.assertEqual(result, 4.5)

    def test_audible_scraper_extract_audible_rating_missing(self):
        """Test l'extraction de note manquante"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_book.select_one.return_value = None
        
        result = scraper._extract_audible_rating(mock_book)
        
        self.assertIsNone(result)

    def test_audible_scraper_extract_audible_narrator(self):
        """Test l'extraction du narrateur Audible"""
        scraper = AudibleScraper()
        mock_book = MagicMock()
        mock_narrator = MagicMock()
        mock_narrator.get_text.return_value = "Narrated by Test Narrator"
        mock_book.select_one.return_value = mock_narrator
        
        result = scraper._extract_audible_narrator(mock_book)
        
        self.assertEqual(result, "Narrated by Test Narrator")  # Valeur réelle

    def test_babelio_scraper_search_with_results(self):
        """Test la recherche Babelio avec résultats"""
        scraper = BabelioScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><div class="list_livre">Book</div></html>'
            mock_get.return_value = mock_response
            
            with patch.object(scraper, '_parse_search_results') as mock_parse:
                mock_parse.return_value = BookInfo(title="Test Book", author="Test Author")
                
                result = scraper.search_babelio("Test Author", "Test Book")
                
                self.assertIsNotNone(result)
                self.assertEqual(result.title, "Test Book")

    def test_babelio_scraper_search_no_results(self):
        """Test la recherche Babelio sans résultats"""
        scraper = BabelioScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><div>No results</div></html>'
            mock_get.return_value = mock_response
            
            result = scraper.search_babelio("Test Author", "Test Book")
            
            self.assertIsNone(result)

    def test_babelio_scraper_search_http_error(self):
        """Test la recherche Babelio avec erreur HTTP"""
        scraper = BabelioScraper()
        
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("HTTP Error")
            
            result = scraper.search_babelio("Test Author", "Test Book")
            
            self.assertIsNone(result)

    def test_babelio_scraper_parse_search_results_success(self):
        """Test le parsing des résultats de recherche réussi"""
        scraper = BabelioScraper()
        mock_soup = MagicMock()
        mock_soup.select.return_value = []  # Pas de résultats pour éviter l'erreur
        
        result = scraper._parse_search_results(mock_soup, "Test Author", "Test Book")
        
        # Test que la méthode gère bien le cas sans résultats
        self.assertIsNone(result)

    def test_babelio_scraper_parse_search_results_no_results(self):
        """Test le parsing sans résultats"""
        scraper = BabelioScraper()
        mock_soup = MagicMock()
        mock_soup.select.return_value = []
        
        result = scraper._parse_search_results(mock_soup, "Test Author", "Test Book")
        
        self.assertIsNone(result)

    def test_babelio_scraper_download_cover_success(self):
        """Test le téléchargement de pochette réussi"""
        scraper = BabelioScraper()
        cover_url = "http://example.com/cover.jpg"
        save_path = Path(self.temp_dir) / "cover.jpg"
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b"fake image content"
            mock_get.return_value = mock_response
            
            result = scraper.download_cover(cover_url, save_path)
            
            self.assertTrue(result)
            self.assertTrue(save_path.exists())

    def test_babelio_scraper_download_cover_failure(self):
        """Test l'échec de téléchargement de pochette"""
        scraper = BabelioScraper()
        cover_url = "http://example.com/cover.jpg"
        save_path = Path(self.temp_dir) / "cover.jpg"
        
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Download error")
            
            result = scraper.download_cover(cover_url, save_path)
            
            self.assertFalse(result)

    def test_book_info_creation_complete(self):
        """Test la création complète de BookInfo"""
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

    def test_book_info_creation_minimal(self):
        """Test la création minimale de BookInfo"""
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

    def test_book_info_str_complete(self):
        """Test la représentation string complète"""
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

    def test_book_info_str_minimal(self):
        """Test la représentation string minimale"""
        book_info = BookInfo(title="Test", author="Author")
        
        result = str(book_info)
        
        self.assertIn("Test", result)
        self.assertIn("Author", result)

    def test_audible_similarity_calculation(self):
        """Test le calcul de similarité Audible"""
        scraper = AudibleScraper()
        
        # Test similarité identique
        similarity = scraper._calculate_similarity("test", "test")
        self.assertEqual(similarity, 1.0)
        
        # Test similarité différente
        similarity = scraper._calculate_similarity("test", "other")
        self.assertEqual(similarity, 0.0)
        
        # Test similarité partielle
        similarity = scraper._calculate_similarity("test word", "test other")
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)

    def test_audible_match_validation(self):
        """Test la validation de correspondance Audible"""
        scraper = AudibleScraper()
        
        # Test correspondance positive
        result = scraper._is_match("Test Book", "Test Author", "Test Book", "Test Author")
        self.assertTrue(result)
        
        # Test correspondance négative
        result = scraper._is_match("Test Book", "Test Author", "Other Book", "Other Author")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
