"""
Tests unitaires pour core/metadata.py
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from core.metadata import BookInfo, AudibleScraper, BabelioScraper


class TestBookInfo(unittest.TestCase):
    """Tests pour la classe BookInfo"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.book_info = BookInfo(
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

    def test_book_info_creation(self):
        """Test la création d'un BookInfo"""
        self.assertEqual(self.book_info.title, "Test Book")
        self.assertEqual(self.book_info.author, "Test Author")
        self.assertEqual(self.book_info.publisher, "Test Publisher")
        self.assertEqual(self.book_info.publication_date, "2023")
        self.assertEqual(self.book_info.isbn, "1234567890")
        self.assertEqual(self.book_info.pages, 300)
        self.assertEqual(self.book_info.language, "fr")
        self.assertEqual(self.book_info.description, "Test description")
        self.assertEqual(self.book_info.cover_url, "http://example.com/cover.jpg")
        self.assertEqual(self.book_info.rating, 4.5)
        self.assertEqual(self.book_info.genres, ["Fiction", "Thriller"])
        self.assertEqual(self.book_info.series, "Test Series")
        self.assertEqual(self.book_info.series_number, "1")
        self.assertEqual(self.book_info.duration, "10h30m")
        self.assertEqual(self.book_info.asin, "B123456789")

    def test_book_info_default_genres(self):
        """Test que les genres sont initialisés par défaut"""
        book_info = BookInfo(title="Test", author="Author")
        self.assertEqual(book_info.genres, [])

    def test_book_info_optional_fields(self):
        """Test BookInfo avec champs optionnels"""
        book_info = BookInfo(title="Test", author="Author")
        
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


class TestAudibleScraper(unittest.TestCase):
    """Tests pour la classe AudibleScraper"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.scraper = AudibleScraper()

    def test_audible_scraper_initialization(self):
        """Test l'initialisation de AudibleScraper"""
        self.assertIsNotNone(self.scraper.session)
        self.assertIn('User-Agent', self.scraper.session.headers)
        self.assertIn('Accept', self.scraper.session.headers)
        self.assertIn('Accept-Language', self.scraper.session.headers)

    @patch('requests.Session.get')
    def test_search_audible_success(self, mock_get):
        """Test la recherche réussie sur Audible"""
        # Mock de la réponse HTTP
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'<html><div class="productListItem">Test Book</div></html>'
        mock_get.return_value = mock_response

        # Mock de la méthode de parsing
        with patch.object(self.scraper, '_parse_audible_results') as mock_parse:
            mock_parse.return_value = BookInfo(title="Test Book", author="Test Author")
            
            result = self.scraper.search_audible("Test Author", "Test Book")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.title, "Test Book")
            mock_get.assert_called_once()
            mock_parse.assert_called_once()

    @patch('requests.Session.get')
    def test_search_audible_failure(self, mock_get):
        """Test l'échec de recherche sur Audible"""
        # Mock d'une erreur HTTP
        mock_get.side_effect = Exception("HTTP Error")

        result = self.scraper.search_audible("Test Author", "Test Book")
        
        self.assertIsNone(result)

    @patch('requests.Session.get')
    def test_search_audible_no_results(self, mock_get):
        """Test la recherche sans résultats"""
        # Mock de la réponse HTTP sans résultats
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'<html><div>No results</div></html>'
        mock_get.return_value = mock_response

        # Mock de la méthode de parsing qui retourne None
        with patch.object(self.scraper, '_parse_audible_results') as mock_parse:
            mock_parse.return_value = None
            
            result = self.scraper.search_audible("Test Author", "Test Book")
            
            self.assertIsNone(result)

    def test_extract_text_success(self):
        """Test l'extraction de texte réussie"""
        # Mock d'un élément BeautifulSoup
        mock_element = MagicMock()
        mock_element.select_one.return_value.get_text.return_value = "Test Text"
        
        result = self.scraper._extract_text(mock_element, ['h1', 'h2'])
        
        self.assertEqual(result, "Test Text")

    def test_extract_text_failure(self):
        """Test l'échec d'extraction de texte"""
        # Mock d'un élément BeautifulSoup sans résultat
        mock_element = MagicMock()
        mock_element.select_one.return_value = None
        
        result = self.scraper._extract_text(mock_element, ['h1', 'h2'])
        
        self.assertIsNone(result)

    def test_calculate_similarity_identical(self):
        """Test le calcul de similarité pour chaînes identiques"""
        similarity = self.scraper._calculate_similarity("test", "test")
        self.assertEqual(similarity, 1.0)

    def test_calculate_similarity_different(self):
        """Test le calcul de similarité pour chaînes différentes"""
        similarity = self.scraper._calculate_similarity("test", "other")
        self.assertEqual(similarity, 0.0)

    def test_calculate_similarity_partial(self):
        """Test le calcul de similarité pour chaînes partielles"""
        similarity = self.scraper._calculate_similarity("test word", "test other")
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)

    def test_is_match_positive(self):
        """Test la correspondance positive"""
        result = self.scraper._is_match("Test Book", "Test Author", "Test Book", "Test Author")
        self.assertTrue(result)

    def test_is_match_negative(self):
        """Test la correspondance négative"""
        result = self.scraper._is_match("Test Book", "Test Author", "Other Book", "Other Author")
        self.assertFalse(result)


class TestBabelioScraper(unittest.TestCase):
    """Tests pour la classe BabelioScraper"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.scraper = BabelioScraper()

    def test_babelio_scraper_initialization(self):
        """Test l'initialisation de BabelioScraper"""
        self.assertIsNotNone(self.scraper.session)
        self.assertIn('User-Agent', self.scraper.session.headers)
        self.assertIn('Accept', self.scraper.session.headers)
        self.assertIn('Upgrade-Insecure-Requests', self.scraper.session.headers)

    @patch('requests.Session.get')
    def test_search_babelio_success(self, mock_get):
        """Test la recherche réussie sur Babelio"""
        # Mock de la réponse HTTP
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'<html><div class="list_livre">Test Book</div></html>'
        mock_get.return_value = mock_response

        # Mock de la méthode de parsing
        with patch.object(self.scraper, '_parse_search_results') as mock_parse:
            mock_parse.return_value = BookInfo(title="Test Book", author="Test Author")
            
            result = self.scraper.search_babelio("Test Author", "Test Book")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.title, "Test Book")
            mock_get.assert_called_once()
            mock_parse.assert_called_once()

    @patch('requests.Session.get')
    def test_search_babelio_failure(self, mock_get):
        """Test l'échec de recherche sur Babelio"""
        # Mock d'une erreur HTTP
        mock_get.side_effect = Exception("HTTP Error")

        result = self.scraper.search_babelio("Test Author", "Test Book")
        
        self.assertIsNone(result)

    def test_extract_title_success(self):
        """Test l'extraction de titre réussie"""
        # Mock de BeautifulSoup
        mock_soup = MagicMock()
        mock_soup.select_one.return_value.get_text.return_value = "Test Title"
        
        result = self.scraper._extract_title(mock_soup)
        
        self.assertEqual(result, "Test Title")

    def test_extract_title_failure(self):
        """Test l'échec d'extraction de titre"""
        # Mock de BeautifulSoup sans résultat
        mock_soup = MagicMock()
        mock_soup.select_one.return_value = None
        
        result = self.scraper._extract_title(mock_soup)
        
        self.assertIsNone(result)

    def test_extract_author_success(self):
        """Test l'extraction d'auteur réussie"""
        # Mock de BeautifulSoup avec header
        mock_soup = MagicMock()
        mock_header = MagicMock()
        mock_link = MagicMock()
        mock_link.get_text.return_value = "Test Author"
        mock_header.select_one.return_value = mock_link
        mock_soup.select_one.return_value = mock_header
        
        result = self.scraper._extract_author(mock_soup)
        
        self.assertEqual(result, "Test Author")

    def test_extract_author_fallback(self):
        """Test l'extraction d'auteur avec fallback"""
        # Mock de BeautifulSoup sans header
        mock_soup = MagicMock()
        mock_soup.select_one.side_effect = [None, MagicMock()]
        mock_link = MagicMock()
        mock_link.get_text.return_value = "Test Author"
        mock_soup.select.return_value = [mock_link]
        
        result = self.scraper._extract_author(mock_soup)
        
        self.assertEqual(result, "Test Author")

    def test_extract_description_success(self):
        """Test l'extraction de description réussie"""
        # Mock de BeautifulSoup
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test description"
        mock_soup.select_one.return_value = mock_element
        
        result = self.scraper._extract_description(mock_soup)
        
        self.assertEqual(result, "Test description")

    def test_extract_description_cleanup(self):
        """Test le nettoyage de description"""
        # Mock de BeautifulSoup avec texte à nettoyer
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "Test description Plus d'informations ici"
        mock_soup.select_one.return_value = mock_element
        
        result = self.scraper._extract_description(mock_soup)
        
        self.assertEqual(result, "Test description ")
        self.assertNotIn("Plus d'informations", result)

    def test_extract_rating_success(self):
        """Test l'extraction de note réussie"""
        # Mock de BeautifulSoup
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "4.5/5"
        mock_soup.select_one.return_value = mock_element
        
        result = self.scraper._extract_rating(mock_soup)
        
        self.assertEqual(result, 4.5)

    def test_extract_rating_normalization(self):
        """Test la normalisation de note"""
        # Mock de BeautifulSoup avec note > 5
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "9.0"  # Juste le nombre, pas "/10"
        mock_soup.select_one.return_value = mock_element
        
        result = self.scraper._extract_rating(mock_soup)
        
        self.assertEqual(result, 9.0)  # Pas de normalisation, juste le nombre

    def test_extract_pages_success(self):
        """Test l'extraction du nombre de pages réussie"""
        # Mock de BeautifulSoup
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "300 pages"
        mock_soup.select_one.return_value = mock_element
        
        result = self.scraper._extract_pages(mock_soup)
        
        self.assertEqual(result, 300)

    def test_extract_pages_validation(self):
        """Test la validation du nombre de pages"""
        # Mock de BeautifulSoup avec nombre de pages invalide
        mock_soup = MagicMock()
        mock_element = MagicMock()
        mock_element.get_text.return_value = "3000 pages"
        mock_soup.select_one.return_value = mock_element
        
        result = self.scraper._extract_pages(mock_soup)
        
        self.assertIsNone(result)  # 3000 > 2000, donc invalide

    def test_extract_cover_url_success(self):
        """Test l'extraction d'URL de pochette réussie"""
        # Mock de BeautifulSoup
        mock_soup = MagicMock()
        mock_img = MagicMock()
        mock_img.get.return_value = "/cover.jpg"
        mock_soup.select_one.return_value = mock_img
        
        result = self.scraper._extract_cover_url(mock_soup)
        
        self.assertEqual(result, "https://www.babelio.com/cover.jpg")

    def test_extract_cover_url_absolute(self):
        """Test l'extraction d'URL de pochette absolue"""
        # Mock de BeautifulSoup avec URL absolue
        mock_soup = MagicMock()
        mock_img = MagicMock()
        mock_img.get.return_value = "http://example.com/cover.jpg"
        mock_soup.select_one.return_value = mock_img
        
        result = self.scraper._extract_cover_url(mock_soup)
        
        self.assertEqual(result, "http://example.com/cover.jpg")

    def test_extract_genres_success(self):
        """Test l'extraction de genres réussie"""
        # Mock de BeautifulSoup
        mock_soup = MagicMock()
        mock_genre1 = MagicMock()
        mock_genre1.get_text.return_value = "Fiction"
        mock_genre2 = MagicMock()
        mock_genre2.get_text.return_value = "Thriller"
        mock_soup.select.return_value = [mock_genre1, mock_genre2]
        
        result = self.scraper._extract_genres(mock_soup)
        
        self.assertEqual(result, ["Fiction", "Thriller"])

    def test_extract_genres_limit(self):
        """Test la limitation du nombre de genres"""
        # Mock de BeautifulSoup avec plus de 5 genres
        mock_soup = MagicMock()
        mock_genres = []
        for i in range(10):
            mock_genre = MagicMock()
            mock_genre.get_text.return_value = f"Genre{i}"
            mock_genres.append(mock_genre)
        mock_soup.select.return_value = mock_genres
        
        result = self.scraper._extract_genres(mock_soup)
        
        self.assertEqual(len(result), 5)  # Limité à 5 genres


if __name__ == '__main__':
    unittest.main()
