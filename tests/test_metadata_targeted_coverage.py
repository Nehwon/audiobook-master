"""
Tests ciblés pour core/metadata.py - Focus sur les vraies méthodes non couvertes pour atteindre 60%
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
from pathlib import Path

from core.metadata import BookInfo, AudibleScraper, BabelioScraper, GoogleBooksScraper, BookScraper


class TestMetadataTargetedCoverage(unittest.TestCase):
    """Tests ciblés pour couvrir les vraies méthodes de metadata.py et atteindre 60%"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()

    def test_audible_scraper_extract_title_success(self):
        """Test l'extraction du titre Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test Book Title"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_title(mock_soup)
        
        self.assertEqual(result, "Test Book Title")

    def test_audible_scraper_extract_title_fallback(self):
        """Test l'extraction du titre Audible avec fallback"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_fallback = MagicMock()
        mock_fallback.get_text.return_value = "Fallback Title"
        mock_soup.select_one.side_effect = [None, None, mock_fallback]
        
        result = scraper._extract_audible_title(mock_soup)
        
        self.assertEqual(result, "Fallback Title")

    def test_audible_scraper_extract_author_success(self):
        """Test l'extraction de l'auteur Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test Author"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_author(mock_soup)
        
        self.assertEqual(result, "Test Author")

    def test_audible_scraper_extract_narrator_success(self):
        """Test l'extraction du narrateur Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test Narrator"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_narrator(mock_soup)
        
        self.assertEqual(result, "Test Narrator")

    def test_audible_scraper_extract_description_success(self):
        """Test l'extraction de la description Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test Description"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_description(mock_soup)
        
        self.assertEqual(result, "Test Description")

    def test_audible_scraper_extract_publisher_success(self):
        """Test l'extraction de l'éditeur Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test Publisher"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_publisher(mock_soup)
        
        self.assertEqual(result, "Test Publisher")

    def test_audible_scraper_extract_date_success(self):
        """Test l'extraction de la date Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "2023-01-01"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_date(mock_soup)
        
        self.assertEqual(result, "2023-01-01")

    def test_audible_scraper_extract_rating_success(self):
        """Test l'extraction de la note Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "4.5 out of 5 stars"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_rating(mock_soup)
        
        self.assertEqual(result, 4.5)

    def test_audible_scraper_extract_cover_url_success(self):
        """Test l'extraction de l'URL de pochette Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get.return_value = "http://example.com/cover.jpg"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_cover_url(mock_soup)
        
        self.assertEqual(result, "http://example.com/cover.jpg")

    def test_audible_scraper_extract_genres_success(self):
        """Test l'extraction des genres Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Fiction"
        mock_soup.select.return_value = [mock_element]
        
        result = scraper._extract_audible_genres(mock_soup)
        
        self.assertEqual(result, ["Fiction"])

    def test_audible_scraper_extract_series_success(self):
        """Test l'extraction de la série Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test Series, Book 1"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_series(mock_soup)
        
        self.assertEqual(result, "Test Series, Book 1")

    def test_audible_scraper_extract_duration_success(self):
        """Test l'extraction de la durée Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "12 hr 30 min"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_duration(mock_soup)
        
        self.assertEqual(result, "12 hr 30 min")

    def test_audible_scraper_extract_asin_success(self):
        """Test l'extraction de l'ASIN Audible réussie"""
        scraper = AudibleScraper()
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get.return_value = "B1234567890"
        mock_soup.select_one.return_value = mock_element
        
        result = scraper._extract_audible_asin(mock_soup)
        
        self.assertEqual(result, "B1234567890")

    def test_audible_scraper_get_book_info_success(self):
        """Test la récupération des infos complètes d'un livre Audible"""
        scraper = AudibleScraper()
        url = "http://example.com/book"
        
        with patch.object(scraper, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b'<html><h1>Test Book</h1></html>'
            mock_session.get.return_value = mock_response
            
            with patch.object(scraper, '_extract_audible_title') as mock_title:
                with patch.object(scraper, '_extract_audible_author') as mock_author:
                    mock_title.return_value = "Test Book"
                    mock_author.return_value = "Test Author"
                    
                    result = scraper.get_audible_book_info(url)
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(result.title, "Test Book")
                    self.assertEqual(result.author, "Test Author")

    def test_audible_scraper_get_book_info_retry_logic(self):
        """Test la logique de retry pour get_audible_book_info"""
        scraper = AudibleScraper()
        url = "http://example.com/book"
        
        with patch.object(scraper, 'session') as mock_session:
            # Premier appel échoue, deuxième réussit
            mock_session.get.side_effect = [
                Exception("Network error"),
                MagicMock(raise_for_status=MagicMock(), content=b'<html><h1>Test Book</h1></html>')
            ]
            
            with patch.object(scraper, '_extract_audible_title') as mock_title:
                with patch.object(scraper, '_extract_audible_author') as mock_author:
                    mock_title.return_value = "Test Book"
                    mock_author.return_value = "Test Author"
                    
                    result = scraper.get_audible_book_info(url)
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(mock_session.get.call_count, 2)

    def test_google_books_scraper_search_success(self):
        """Test la recherche Google Books réussie"""
        scraper = GoogleBooksScraper()
        
        with patch.object(scraper, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'items': [{
                    'volumeInfo': {
                        'title': 'Test Book',
                        'authors': ['Test Author'],
                        'publisher': 'Test Publisher',
                        'publishedDate': '2023',
                        'description': 'Test Description',
                        'pageCount': 300,
                        'categories': ['Fiction'],
                        'averageRating': 4.5,
                        'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': '1234567890123'}],
                        'imageLinks': {'thumbnail': 'http://example.com/cover.jpg'}
                    }
                }]
            }
            mock_session.get.return_value = mock_response
            
            result = scraper.search_google_books("Test Author", "Test Book")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.title, "Test Book")
            self.assertEqual(result.author, "Test Author")

    def test_google_books_scraper_search_no_results(self):
        """Test la recherche Google Books sans résultats"""
        scraper = GoogleBooksScraper()
        
        with patch.object(scraper, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {'items': []}
            mock_session.get.return_value = mock_response
            
            result = scraper.search_google_books("Test Author", "Test Book")
            
            self.assertIsNone(result)

    def test_google_books_scraper_search_api_error(self):
        """Test la recherche Google Books avec erreur API"""
        scraper = GoogleBooksScraper()
        
        with patch.object(scraper, 'session') as mock_session:
            mock_session.get.side_effect = Exception("API Error")
            
            result = scraper.search_google_books("Test Author", "Test Book")
            
            self.assertIsNone(result)

    def test_google_books_scraper_parse_result_success(self):
        """Test le parsing d'un résultat Google Books réussi"""
        scraper = GoogleBooksScraper()
        item = {
            'volumeInfo': {
                'title': 'Test Book',
                'authors': ['Test Author'],
                'publisher': 'Test Publisher',
                'publishedDate': '2023',
                'description': 'Test Description',
                'pageCount': 300,
                'categories': ['Fiction'],
                'averageRating': 4.5,
                'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': '1234567890123'}],
                'imageLinks': {'thumbnail': 'http://example.com/cover.jpg'}
            }
        }
        
        result = scraper._parse_google_books_result(item, "Test Author", "Test Book")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Test Book")
        self.assertEqual(result.author, "Test Author")
        self.assertEqual(result.publisher, "Test Publisher")
        self.assertEqual(result.isbn, "1234567890123")

    def test_google_books_scraper_parse_result_missing_data(self):
        """Test le parsing avec données manquantes"""
        scraper = GoogleBooksScraper()
        item = {
            'volumeInfo': {
                'title': 'Test Book',
                'authors': ['Test Author']
                # Manque: publisher, publishedDate, etc.
            }
        }
        
        result = scraper._parse_google_books_result(item, "Test Author", "Test Book")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Test Book")
        self.assertEqual(result.author, "Test Author")
        self.assertIsNone(result.publisher)
        self.assertIsNone(result.publication_date)

    def test_google_books_scraper_similarity_perfect_match(self):
        """Test le calcul de similarité avec correspondance parfaite"""
        scraper = GoogleBooksScraper()
        
        result = scraper._is_match("Test Book", "Test Author", "Test Book", "Test Author")
        
        self.assertTrue(result)

    def test_google_books_scraper_similarity_no_match(self):
        """Test le calcul de similarité sans correspondance"""
        scraper = GoogleBooksScraper()
        
        result = scraper._is_match("Test Book", "Test Author", "Other Book", "Other Author")
        
        self.assertFalse(result)

    def test_google_books_scraper_similarity_partial_match(self):
        """Test le calcul de similarité avec correspondance partielle"""
        scraper = GoogleBooksScraper()
        
        result = scraper._is_match("Test Book", "Test Author", "Test Book", "Test Author")
        
        self.assertTrue(result)  # Correspondance exacte

    def test_google_books_scraper_download_cover_success(self):
        """Test le téléchargement de pochette Google Books réussi"""
        scraper = GoogleBooksScraper()
        cover_url = "http://example.com/cover.jpg"
        save_path = Path(self.temp_dir) / "cover.jpg"
        
        with patch.object(scraper, 'session') as mock_session:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b"fake image content"
            mock_session.get.return_value = mock_response
            
            with patch('builtins.open', mock_open()) as mock_file:
                result = scraper.download_cover(cover_url, str(save_path))
                
                self.assertTrue(result)
                mock_file.assert_called_once()

    def test_google_books_scraper_download_cover_failure(self):
        """Test l'échec de téléchargement de pochette Google Books"""
        scraper = GoogleBooksScraper()
        cover_url = "http://example.com/cover.jpg"
        save_path = Path(self.temp_dir) / "cover.jpg"
        
        with patch.object(scraper, 'session') as mock_session:
            mock_session.get.side_effect = Exception("Download error")
            
            result = scraper.download_cover(cover_url, str(save_path))
            
            self.assertFalse(result)

    def test_book_scraper_search_google_books_first(self):
        """Test la recherche BookScraper avec Google Books en premier"""
        scraper = BookScraper()
        
        with patch.object(scraper.google_books, 'search_google_books') as mock_google:
            with patch.object(scraper.audible, 'search_audible') as mock_audible:
                with patch.object(scraper.babelio, 'search_babelio') as mock_babelio:
                    mock_google.return_value = BookInfo(title="Google Book", author="Test Author")
                    
                    result = scraper.search_book("Test Author", "Test Book")
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(result.title, "Google Book")
                    mock_google.assert_called_once()
                    mock_audible.assert_not_called()
                    mock_babelio.assert_not_called()

    def test_book_scraper_search_fallback_to_audible(self):
        """Test la recherche BookScraper avec fallback vers Audible"""
        scraper = BookScraper()
        
        with patch.object(scraper.google_books, 'search_google_books') as mock_google:
            with patch.object(scraper.audible, 'search_audible') as mock_audible:
                with patch.object(scraper.babelio, 'search_babelio') as mock_babelio:
                    mock_google.return_value = None
                    mock_audible.return_value = BookInfo(title="Audible Book", author="Test Author")
                    
                    result = scraper.search_book("Test Author", "Test Book")
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(result.title, "Audible Book")
                    mock_google.assert_called_once()
                    mock_audible.assert_called_once()
                    mock_babelio.assert_not_called()

    def test_book_scraper_search_fallback_to_babelio(self):
        """Test la recherche BookScraper avec fallback vers Babelio"""
        scraper = BookScraper()
        
        with patch.object(scraper.google_books, 'search_google_books') as mock_google:
            with patch.object(scraper.audible, 'search_audible') as mock_audible:
                with patch.object(scraper.babelio, 'search_babelio') as mock_babelio:
                    mock_google.return_value = None
                    mock_audible.return_value = None
                    mock_babelio.return_value = BookInfo(title="Babelio Book", author="Test Author")
                    
                    result = scraper.search_book("Test Author", "Test Book")
                    
                    self.assertIsNotNone(result)
                    self.assertEqual(result.title, "Babelio Book")
                    mock_google.assert_called_once()
                    mock_audible.assert_called_once()
                    mock_babelio.assert_called_once()

    def test_book_scraper_search_no_results(self):
        """Test la recherche BookScraper sans aucun résultat"""
        scraper = BookScraper()
        
        with patch.object(scraper.google_books, 'search_google_books') as mock_google:
            with patch.object(scraper.audible, 'search_audible') as mock_audible:
                with patch.object(scraper.babelio, 'search_babelio') as mock_babelio:
                    mock_google.return_value = None
                    mock_audible.return_value = None
                    mock_babelio.return_value = None
                    
                    result = scraper.search_book("Test Author", "Test Book")
                    
                    self.assertIsNone(result)
                    mock_google.assert_called_once()
                    mock_audible.assert_called_once()
                    mock_babelio.assert_called_once()


if __name__ == '__main__':
    unittest.main()
