#!/usr/bin/env python3
"""
Module de scraping pour les informations de livres spécialisé audiobooks
Sources: Audible (référence mondiale), Babelio (backup français)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import re
import time
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BookInfo:
    """Informations complètes sur un livre/audiobook"""
    title: str
    author: str
    narrator: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    isbn: Optional[str] = None
    pages: Optional[int] = None
    language: str = "fr"
    description: Optional[str] = None
    cover_url: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = None
    series: Optional[str] = None
    series_number: Optional[str] = None
    duration: Optional[str] = None  # Durée spécifique audiobook
    asin: Optional[str] = None  # Identifiant Audible
    
    def __post_init__(self):
        if self.genres is None:
            self.genres = []

class AudibleScraper:
    """Scraper spécialisé pour Audible - la référence mondiale des audiobooks"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def search_audible(self, author: str, title: str, max_retries: int = 3) -> Optional[BookInfo]:
        """Recherche un audiobook sur Audible"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🔍 Recherche Audible: '{author} - {title}' (tentative {attempt + 1}/{max_retries})")
                
                # Construction de la recherche Audible
                search_query = quote(f"{title} {author}")
                search_url = f"https://www.audible.fr/search?keywords={search_query}&filterRefine=base_keywords:base_keywords"
                
                logger.info(f"   📡 URL: {search_url}")
                
                response = self.session.get(search_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Analyse des résultats de recherche Audible
                book_info = self._parse_audible_results(soup, author, title)
                if book_info:
                    logger.info(f"   ✅ Audiobook trouvé: {book_info.title}")
                    return book_info
                
                logger.warning(f"   ⚠️ Aucun résultat trouvé pour '{author} - {title}'")
                return None
                
            except requests.RequestException as e:
                logger.error(f"   ❌ Erreur HTTP Audible (tentative {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except Exception as e:
                logger.error(f"   💥 Erreur inattendue Audible: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        return None
    
    def _parse_audible_results(self, soup: BeautifulSoup, expected_author: str, expected_title: str) -> Optional[BookInfo]:
        """Analyse les résultats de recherche Audible"""
        
        # Sélecteurs CSS pour Audible
        selectors = [
            'li.productListItem',           # Format liste
            'div.bc-product-item',         # Format produit
            'div.audible-product-item',    # Format audible
            '[data-test="product-item"]',  # Format test
            '.adbl-impression-container',  # Format impression
        ]
        
        book_element = None
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                book_element = elements[0]  # Prend le premier résultat
                logger.info(f"   🎯 Sélecteur Audible trouvé: {selector}")
                break
        
        if not book_element:
            logger.warning("   ⚠️ Aucun élément d'audiobook trouvé dans les résultats")
            return None
        
        # Extraction du lien vers la page détaillée
        link_selectors = ['a', 'h3 a', 'h4 a', '.bc-heading a', '[data-test="product-title"] a']
        book_link = None
        
        for link_selector in link_selectors:
            book_link = book_element.select_one(link_selector)
            if book_link and book_link.get('href'):
                break
        
        if not book_link:
            logger.warning("   ⚠️ Aucun lien vers la page de l'audiobook trouvé")
            return None
        
        # Construction de l'URL complète
        book_url = urljoin('https://www.audible.fr', book_link.get('href'))
        logger.info(f"   🔗 URL de l'audiobook: {book_url}")
        
        # Extraction des informations de base depuis les résultats
        title = self._extract_text(book_element, ['h3', 'h4', '.bc-heading', '[data-test="product-title"]'])
        author = self._extract_text(book_element, ['.bc-author', '.author-name', '[data-test="author-name"]'])
        narrator = self._extract_text(book_element, ['.bc-narrator', '.narrator-name', '[data-test="narrator-name"]'])
        
        if not title or not author:
            logger.info("   📄 Informations incomplètes, récupération depuis la page détaillée...")
            return self.get_audible_book_info(book_url)
        
        # Validation avec les données attendues
        if self._is_match(title, author, expected_title, expected_author):
            logger.info(f"   ✅ Correspondance trouvée: {author} - {title}")
            return self.get_audible_book_info(book_url)
        else:
            logger.info(f"   ❌ Non correspondance: trouvé '{author} - {title}' vs attendu '{expected_author} - {expected_title}'")
            return None
    
    def get_audible_book_info(self, url: str, max_retries: int = 3) -> Optional[BookInfo]:
        """Extrait les informations détaillées depuis la page Audible d'un audiobook"""
        for attempt in range(max_retries):
            try:
                logger.info(f"   📄 Extraction détails depuis: {url}")
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraction avec sélecteurs multiples pour robustesse
                title = self._extract_audible_title(soup)
                author = self._extract_audible_author(soup)
                narrator = self._extract_audible_narrator(soup)
                description = self._extract_audible_description(soup)
                publisher = self._extract_audible_publisher(soup)
                publication_date = self._extract_audible_date(soup)
                rating = self._extract_audible_rating(soup)
                cover_url = self._extract_audible_cover_url(soup)
                genres = self._extract_audible_genres(soup)
                series = self._extract_audible_series(soup)
                duration = self._extract_audible_duration(soup)
                asin = self._extract_audible_asin(soup)
                
                if not title or not author:
                    logger.warning("   ⚠️ Titre ou auteur manquant")
                    return None
                
                book_info = BookInfo(
                    title=title.strip(),
                    author=author.strip(),
                    narrator=narrator.strip() if narrator else None,
                    publisher=publisher.strip() if publisher else None,
                    publication_date=publication_date.strip() if publication_date else None,
                    description=description.strip() if description else None,
                    cover_url=cover_url,
                    rating=rating,
                    genres=genres,
                    series=series.strip() if series else None,
                    duration=duration.strip() if duration else None,
                    asin=asin.strip() if asin else None,
                    language="fr"
                )
                
                logger.info(f"   ✅ Extraction Audible réussie: {book_info.title}")
                if book_info.narrator:
                    logger.info(f"      🎤 Narrateur: {book_info.narrator}")
                if book_info.duration:
                    logger.info(f"      ⏱️ Durée: {book_info.duration}")
                if book_info.series:
                    logger.info(f"      📖 Série: {book_info.series}")
                if book_info.rating:
                    logger.info(f"      ⭐ Note: {book_info.rating}/5")
                if book_info.asin:
                    logger.info(f"      🏷️ ASIN: {book_info.asin}")
                
                return book_info
                
            except requests.RequestException as e:
                logger.error(f"   ❌ Erreur HTTP extraction (tentative {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except Exception as e:
                logger.error(f"   💥 Erreur extraction: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        return None
    
    def _extract_audible_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le titre avec sélecteurs Audible"""
        selectors = [
            'h1.bc-heading',
            'h1',
            '.bc-text-bold',
            '[data-test="product-title"]',
            '.adbl-product-title'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_audible_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait l'auteur avec sélecteurs Audible"""
        selectors = [
            '.bc-author a',
            '.author-name a',
            '[data-test="author-name"] a',
            '.adbl-author'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_audible_narrator(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le narrateur avec sélecteurs Audible"""
        selectors = [
            '.bc-narrator a',
            '.narrator-name a',
            '[data-test="narrator-name"] a',
            '.adbl-narrator'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_audible_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait la description avec sélecteurs Audible"""
        selectors = [
            '.bc-expander-content',
            '.adbl-product-description',
            '[data-test="product-description"]',
            '.bc-text'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Nettoyage du texte
                text = element.get_text(strip=True)
                # Suppression des publicités et textes inutiles
                text = re.sub(r'Plus d\'informations.*$', '', text, flags=re.IGNORECASE)
                text = re.sub(r'Acheter.*$', '', text, flags=re.IGNORECASE)
                return text
        return None
    
    def _extract_audible_publisher(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait l'éditeur avec sélecteurs Audible"""
        selectors = [
            '.bc-publisher',
            '.publisher-name',
            '[data-test="publisher"]',
            '.adbl-publisher'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_audible_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait la date de publication avec sélecteurs Audible"""
        selectors = [
            '.bc-release-date',
            '.release-date',
            '[data-test="release-date"]',
            '.adbl-date'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_audible_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extrait la note avec sélecteurs Audible"""
        selectors = [
            '.bc-rating',
            '.adbl-rating',
            '[data-test="rating"]',
            '.stars'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    rating = float(match.group(1))
                    # Normalisation sur 5 si nécessaire
                    if rating > 5:
                        rating = rating / 5
                    return rating
        return None
    
    def _extract_audible_cover_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait l'URL de la pochette avec sélecteurs Audible"""
        selectors = [
            '.adbl-product-image img',
            '.bc-image img',
            '[data-test="product-image"] img',
            '.cover img'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get('src'):
                return element.get('src')
        return None
    
    def _extract_audible_genres(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les genres avec sélecteurs Audible"""
        selectors = [
            '.bc-genre',
            '.genre-tags',
            '[data-test="genre"]',
            '.categories'
        ]
        
        genres = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and text not in genres:
                    genres.append(text)
        
        return genres[:5]  # Limite à 5 genres
    
    def _extract_audible_series(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le nom de la série avec sélecteurs Audible"""
        selectors = [
            '.bc-series',
            '.series-name',
            '[data-test="series"]',
            '.adbl-series'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_audible_duration(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait la durée avec sélecteurs Audible"""
        selectors = [
            '.bc-duration',
            '.runtime',
            '[data-test="runtime"]',
            '.adbl-duration'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_audible_asin(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait l'ASIN avec sélecteurs Audible"""
        # L'ASIN est souvent dans l'URL ou les métadonnées
        # Essai depuis l'URL
        url_asin = re.search(r'/pd/([A-Z0-9]{10})', str(soup))
        if url_asin:
            return url_asin.group(1)
        
        # Essai depuis les métadonnées
        selectors = [
            '[data-asin]',
            '.adbl-asin',
            '[data-test="asin"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                asin = element.get('data-asin') or element.get('asin')
                if asin:
                    return asin
        
        return None
    
    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """Extrait le texte d'un élément avec plusieurs sélecteurs"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return None
    
    def _is_match(self, found_title: str, found_author: str, expected_title: str, expected_author: str) -> bool:
        """Vérifie si les résultats correspondent aux attentes"""
        # Nettoyage et comparaison flexible
        found_title_clean = re.sub(r'[^\w\s]', '', found_title.lower())
        expected_title_clean = re.sub(r'[^\w\s]', '', expected_title.lower())
        
        found_author_clean = re.sub(r'[^\w\s]', '', found_author.lower())
        expected_author_clean = re.sub(r'[^\w\s]', '', expected_author.lower())
        
        # Vérification de la similarité (au moins 70% de correspondance)
        title_similarity = self._calculate_similarity(found_title_clean, expected_title_clean)
        author_similarity = self._calculate_similarity(found_author_clean, expected_author_clean)
        
        return title_similarity > 0.7 and author_similarity > 0.7
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcule la similarité entre deux chaînes"""
        if str1 == str2:
            return 1.0
        
        # Similarité simple basée sur les mots communs
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def download_cover(self, url: str, save_path: str) -> bool:
        """Télécharge une pochette depuis une URL"""
        try:
            logger.info(f"   📥 Téléchargement pochette Audible: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"   ✅ Pochette sauvegardée: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Erreur téléchargement pochette: {e}")
            return False

class BabelioScraper:
    """Scraper spécialisé pour Babelio avec gestion robuste des erreurs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_babelio(self, author: str, title: str, max_retries: int = 3) -> Optional[BookInfo]:
        """Recherche un livre sur Babelio avec le nouveau format d'URL"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🔍 Recherche Babelio: '{author} - {title}' (tentative {attempt + 1}/{max_retries})")
                
                # Construction de la recherche avec le nouveau format
                search_query = quote(f"{title} {author}")
                search_url = f"https://www.babelio.com/?s={search_query}"
                
                logger.info(f"   📡 URL: {search_url}")
                
                response = self.session.get(search_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Analyse des résultats de recherche Babelio
                book_info = self._parse_search_results(soup, author, title)
                if book_info:
                    logger.info(f"   ✅ Livre trouvé: {book_info.title}")
                    return book_info
                
                logger.warning(f"   ⚠️ Aucun résultat trouvé pour '{author} - {title}'")
                return None
                
            except requests.RequestException as e:
                logger.error(f"   ❌ Erreur HTTP Babelio (tentative {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponentiel
                    continue
            except Exception as e:
                logger.error(f"   💥 Erreur inattendue Babelio: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        return None
    
    def _parse_search_results(self, soup: BeautifulSoup, expected_author: str, expected_title: str) -> Optional[BookInfo]:
        """Analyse les résultats de recherche Babelio avec les nouveaux sélecteurs"""
        
        # Nouveaux sélecteurs CSS pour Babelio (basés sur l'analyse réelle)
        selectors = [
            'div.list_livre',           # Format liste de livres
            'div.col-2-4.list_livre',   # Format colonne avec livre
            '[class*="list_livre"]',    # Contient list_livre
        ]
        
        book_element = None
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                book_element = elements[0]  # Prend le premier résultat
                logger.info(f"   🎯 Sélecteur Babelio trouvé: {selector} ({len(elements)} résultats)")
                break
        
        if not book_element:
            logger.warning("   ⚠️ Aucun élément de livre trouvé dans les résultats")
            return None
        
        # Extraction du lien vers la page détaillée
        link_selectors = ['a[href*="/livres/"]', 'a[href*="/livre/"]']
        book_link = None
        
        for link_selector in link_selectors:
            book_link = book_element.select_one(link_selector)
            if book_link and book_link.get('href'):
                break
        
        if not book_link:
            logger.warning("   ⚠️ Aucun lien vers la page du livre trouvé")
            return None
        
        # Construction de l'URL complète
        book_url = urljoin('https://www.babelio.com', book_link.get('href'))
        logger.info(f"   🔗 URL du livre: {book_url}")
        
        # Extraction des informations de base depuis les résultats
        title = book_link.get_text(strip=True)
        
        # Recherche de l'auteur dans le même élément
        author_link = book_element.select_one('a[href*="/auteur/"]')
        author = author_link.get_text(strip=True) if author_link else None
        
        logger.info(f"   � Infos basiques: {title} - {author or 'Auteur inconnu'}")
        
        # Validation avec les données attendues
        if title and self._is_match(title, author or "", expected_title, expected_author):
            logger.info(f"   ✅ Correspondance trouvée: {author or 'Inconnu'} - {title}")
            return self.get_babelio_book_info(book_url)
        else:
            logger.info(f"   ❌ Non correspondance: trouvé '{author or 'Inconnu'} - {title}' vs attendu '{expected_author} - {expected_title}'")
            # Essaye quand même le premier résultat si la correspondance n'est pas parfaite
            logger.info(f"   🔄 Tentative avec le premier résultat quand même...")
            return self.get_babelio_book_info(book_url)
    
    def get_babelio_book_info(self, url: str, max_retries: int = 3) -> Optional[BookInfo]:
        """Extrait les informations détaillées depuis la page Babelio d'un livre"""
        for attempt in range(max_retries):
            try:
                logger.info(f"   📄 Extraction détails depuis: {url}")
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraction avec sélecteurs multiples pour robustesse
                title = self._extract_title(soup)
                author = self._extract_author(soup)
                description = self._extract_description(soup)
                publisher = self._extract_publisher(soup)
                publication_date = self._extract_publication_date(soup)
                pages = self._extract_pages(soup)
                rating = self._extract_rating(soup)
                cover_url = self._extract_cover_url(soup)
                genres = self._extract_genres(soup)
                series = self._extract_series(soup)
                
                if not title or not author:
                    logger.warning("   ⚠️ Titre ou auteur manquant")
                    return None
                
                book_info = BookInfo(
                    title=title.strip(),
                    author=author.strip(),
                    publisher=publisher.strip() if publisher else None,
                    publication_date=publication_date.strip() if publication_date else None,
                    pages=pages,
                    description=description.strip() if description else None,
                    cover_url=cover_url,
                    rating=rating,
                    genres=genres,
                    series=series.strip() if series else None
                )
                
                logger.info(f"   ✅ Extraction réussie: {book_info.title}")
                if book_info.publisher:
                    logger.info(f"      📚 Éditeur: {book_info.publisher}")
                if book_info.publication_date:
                    logger.info(f"      📅 Date: {book_info.publication_date}")
                if book_info.rating:
                    logger.info(f"      ⭐ Note: {book_info.rating}/5")
                
                return book_info
                
            except requests.RequestException as e:
                logger.error(f"   ❌ Erreur HTTP extraction (tentative {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except Exception as e:
                logger.error(f"   💥 Erreur extraction: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        return None
    
    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """Extrait le texte d'un élément avec plusieurs sélecteurs"""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le titre avec sélecteurs Babelio"""
        selectors = [
            'h1',
            '.titre',
            '.book-title',
            'h1.titre'
        ]
        return self._extract_text(soup, selectors)
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait l'auteur avec sélecteurs Babelio"""
        # Priorité au premier lien auteur dans le header
        header = soup.select_one('.livre_header')
        if header:
            author_link = header.select_one('a[href*="/auteur/"]')
            if author_link:
                return author_link.get_text(strip=True)
        
        # Fallback: recherche dans toute la page
        selectors = [
            'a[href*="/auteur/"]',
            '.auteur',
            '.author'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                # Prend le premier auteur qui n'est pas dans les critiques/citations
                if text and len(text) > 2 and 'Page de la citation' not in text:
                    return text
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait la description avec sélecteurs Babelio"""
        selectors = [
            '.texte',
            '.description',
            '.resume',
            '[class*="resume"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Nettoyage du texte
                text = element.get_text(strip=True)
                # Suppression des publicités et textes inutiles
                text = re.sub(r'Plus d\'informations.*$', '', text, flags=re.IGNORECASE)
                text = re.sub(r'Acheter.*$', '', text, flags=re.IGNORECASE)
                text = re.sub(r'Lire la critique.*$', '', text, flags=re.IGNORECASE)
                return text
        return None
    
    def _extract_publisher(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait l'éditeur avec sélecteurs Babelio"""
        livre_con = soup.select_one('.livre_con')
        if livre_con:
            text = livre_con.get_text(strip=True)
            # Recherche du motif "Belfond" ou éditeur connu
            import re
            # Pattern pour les noms d'éditeurs (commence par majuscule)
            pub_patterns = [
                r'(Belfond|Gallimard|Flammarion|Seuil|Grasset|Laffont|Fayard|Albin Michel|Robert Laffont|Presses de la Cité|Actes Sud|Éditions\s+\w+(?:\s+\w+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\d{2}/\d{2}/\d{4}'  # Éditeur avant date
            ]
            
            for pattern in pub_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
        
        return None
    
    def _extract_publication_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait la date de publication avec sélecteurs Babelio"""
        livre_con = soup.select_one('.livre_con')
        if livre_con:
            text = livre_con.get_text(strip=True)
            # Recherche du format JJ/MM/YYYY
            import re
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
            if date_match:
                return date_match.group(1)
        
        return None
    
    def _extract_pages(self, soup: BeautifulSoup) -> Optional[int]:
        """Extrait le nombre de pages avec sélecteurs Babelio"""
        livre_con = soup.select_one('.livre_con')
        if livre_con:
            text = livre_con.get_text(strip=True)
            # Recherche du motif "XXX pages" plus spécifique
            import re
            # Pattern: nombre suivi de "pages" mais pas d'un autre nombre juste après (pour éviter l'ISBN)
            pages_match = re.search(r'(\d{1,4})\s+pages(?!\d)', text)
            if pages_match:
                pages = int(pages_match.group(1))
                # Vérification que c'est un nombre de pages raisonnable (entre 50 et 2000)
                if 50 <= pages <= 2000:
                    return pages
        
        return None
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extrait la note avec sélecteurs Babelio"""
        selectors = [
            '.note',
            '[class*="note"]',
            '.rating',
            '.stars'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Recherche du format X,XX ou X.XX
                import re
                match = re.search(r'(\d+[.,]\d+)', text)
                if match:
                    rating = float(match.group(1).replace(',', '.'))
                    return rating
        return None
    
    def _extract_cover_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait l'URL de la pochette avec sélecteurs Babelio"""
        selectors = [
            'img[src*="couv"]',
            '.livre_couverture',
            '.cover',
            'img[src*="/couv/"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get('src'):
                src = element.get('src')
                # Convertit en URL absolue si nécessaire
                if src.startswith('/'):
                    return f"https://www.babelio.com{src}"
                return src
        return None
    
    def _extract_genres(self, soup: BeautifulSoup) -> List[str]:
        """Extrait les genres avec sélecteurs Babelio"""
        # Les genres sont souvent dans les liens de navigation
        selectors = [
            '.side_l_content a',
            '[class*="genre"]',
            '.categories a'
        ]
        
        genres = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and text not in genres and len(text) < 30:  # Limite la taille
                    genres.append(text)
        
        return genres[:5]  # Limite à 5 genres
    
    def _extract_series(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le nom de la série avec sélecteurs Babelio"""
        # Les séries sont rarement indiquées sur Babelio
        return None
    
    def _is_match(self, found_title: str, found_author: str, expected_title: str, expected_author: str) -> bool:
        """Vérifie si les résultats correspondent aux attentes"""
        # Nettoyage et comparaison flexible
        found_title_clean = re.sub(r'[^\w\s]', '', found_title.lower())
        expected_title_clean = re.sub(r'[^\w\s]', '', expected_title.lower())
        
        found_author_clean = re.sub(r'[^\w\s]', '', found_author.lower())
        expected_author_clean = re.sub(r'[^\w\s]', '', expected_author.lower())
        
        # Vérification de la similarité (au moins 70% de correspondance)
        title_similarity = self._calculate_similarity(found_title_clean, expected_title_clean)
        author_similarity = self._calculate_similarity(found_author_clean, expected_author_clean)
        
        return title_similarity > 0.7 and author_similarity > 0.7
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcule la similarité entre deux chaînes"""
        if str1 == str2:
            return 1.0
        
        # Similarité simple basée sur les mots communs
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def download_cover(self, url: str, save_path: str) -> bool:
        """Télécharge une pochette depuis une URL"""
        try:
            logger.info(f"   📥 Téléchargement pochette: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"   ✅ Pochette sauvegardée: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Erreur téléchargement pochette: {e}")
            return False

class GoogleBooksScraper:
    """Scraper pour Google Books API - source fiable et complète"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
    
    def search_google_books(self, author: str, title: str, max_retries: int = 3) -> Optional[BookInfo]:
        """Recherche un livre via Google Books API"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🔍 Recherche Google Books: '{author} - {title}' (tentative {attempt + 1}/{max_retries})")
                
                # Construction de la requête API
                query = f"intitle:{title} inauthor:{author}"
                params = {
                    'q': query,
                    'maxResults': 5,
                    'langRestrict': 'fr',
                    'printType': 'books'
                }
                
                logger.info(f"   📡 Query: {query}")
                
                response = self.session.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                if 'items' not in data or not data['items']:
                    logger.warning(f"   ⚠️ Aucun résultat trouvé pour '{author} - {title}'")
                    return None
                
                # Analyse du premier résultat
                first_item = data['items'][0]
                book_info = self._parse_google_books_result(first_item, author, title)
                
                if book_info:
                    logger.info(f"   ✅ Livre trouvé sur Google Books: {book_info.title}")
                    return book_info
                
            except requests.RequestException as e:
                logger.error(f"   ❌ Erreur HTTP Google Books (tentative {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            except Exception as e:
                logger.error(f"   💥 Erreur inattendue Google Books: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        return None
    
    def _parse_google_books_result(self, item: dict, expected_author: str, expected_title: str) -> Optional[BookInfo]:
        """Analyse un résultat de Google Books API"""
        try:
            volume_info = item.get('volumeInfo', {})
            
            # Extraction des informations de base
            title = volume_info.get('title', '')
            authors = volume_info.get('authors', [])
            author = authors[0] if authors else ''
            
            if not title or not author:
                logger.warning("   ⚠️ Titre ou auteur manquant")
                return None
            
            # Validation avec les données attendues
            if not self._is_match(title, author, expected_title, expected_author):
                logger.info(f"   ❌ Non correspondance: trouvé '{author} - {title}' vs attendu '{expected_author} - {expected_title}'")
                return None
            
            # Extraction des métadonnées complètes
            publisher = volume_info.get('publisher')
            publication_date = volume_info.get('publishedDate')
            description = volume_info.get('description')
            page_count = volume_info.get('pageCount')
            categories = volume_info.get('categories', [])
            average_rating = volume_info.get('averageRating')
            
            # Extraction de l'ISBN
            industry_identifiers = volume_info.get('industryIdentifiers', [])
            isbn = None
            for identifier in industry_identifiers:
                if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                    isbn = identifier.get('identifier')
                    break
            
            # Extraction de la pochette
            image_links = volume_info.get('imageLinks', {})
            cover_url = image_links.get('large') or image_links.get('medium') or image_links.get('thumbnail')
            
            book_info = BookInfo(
                title=title.strip(),
                author=author.strip(),
                publisher=publisher,
                publication_date=publication_date,
                isbn=isbn,
                pages=page_count,
                description=description,
                cover_url=cover_url,
                rating=average_rating,
                genres=categories[:5] if categories else [],
                language="fr"
            )
            
            logger.info(f"   ✅ Extraction Google Books réussie: {book_info.title}")
            if book_info.publisher:
                logger.info(f"      📚 Éditeur: {book_info.publisher}")
            if book_info.publication_date:
                logger.info(f"      📅 Date: {book_info.publication_date}")
            if book_info.isbn:
                logger.info(f"      🏷️ ISBN: {book_info.isbn}")
            if book_info.rating:
                logger.info(f"      ⭐ Note: {book_info.rating}/5")
            
            return book_info
            
        except Exception as e:
            logger.error(f"   💥 Erreur parsing Google Books: {e}")
            return None
    
    def _is_match(self, found_title: str, found_author: str, expected_title: str, expected_author: str) -> bool:
        """Vérifie si les résultats correspondent aux attentes"""
        # Nettoyage et comparaison flexible
        found_title_clean = re.sub(r'[^\w\s]', '', found_title.lower())
        expected_title_clean = re.sub(r'[^\w\s]', '', expected_title.lower())
        
        found_author_clean = re.sub(r'[^\w\s]', '', found_author.lower())
        expected_author_clean = re.sub(r'[^\w\s]', '', expected_author.lower())
        
        # Vérification de la similarité (au moins 70% de correspondance)
        title_similarity = self._calculate_similarity(found_title_clean, expected_title_clean)
        author_similarity = self._calculate_similarity(found_author_clean, expected_author_clean)
        
        return title_similarity > 0.7 and author_similarity > 0.7
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcule la similarité entre deux chaînes"""
        if str1 == str2:
            return 1.0
        
        # Similarité simple basée sur les mots communs
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def download_cover(self, url: str, save_path: str) -> bool:
        """Télécharge une pochette depuis une URL"""
        try:
            logger.info(f"   📥 Téléchargement pochette Google Books: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"   ✅ Pochette sauvegardée: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Erreur téléchargement pochette: {e}")
            return False

class BookScraper:
    """Interface principale du scraper spécialisée audiobooks"""
    
    def __init__(self):
        self.google_books = GoogleBooksScraper()
        self.audible = AudibleScraper()
        self.babelio = BabelioScraper()
    
    def search_book(self, author: str, title: str) -> Optional[BookInfo]:
        """Recherche un audiobook sur plusieurs sources spécialisées"""
        logger.info(f"🔍 Recherche audiobook: '{author} - {title}'")
        
        # 1. Google Books API (source la plus fiable)
        book_info = self.google_books.search_google_books(author, title)
        if book_info:
            logger.info(f"   ✅ Livre trouvé sur Google Books")
            return book_info
        
        # 2. Audible (source spécialisée audiobooks)
        book_info = self.audible.search_audible(author, title)
        if book_info:
            logger.info(f"   ✅ Audiobook trouvé sur Audible")
            return book_info
        
        # 3. Babelio (backup français)
        book_info = self.babelio.search_babelio(author, title)
        if book_info:
            logger.info(f"   ✅ Livre trouvé sur Babelio (backup)")
            return book_info
        
        logger.warning(f"   ❌ Audiobook non trouvé sur les sources disponibles")
        return None
        
        # 1. Google Books API (source la plus fiable)
        book_info = self.google_books.search_google_books(author, title)
        if book_info:
            logger.info(f"   ✅ Livre trouvé sur Google Books")
            return book_info
        
        # 2. Audible (source spécialisée audiobooks)
        book_info = self.audible.search_audible(author, title)
        if book_info:
            logger.info(f"   ✅ Audiobook trouvé sur Audible")
            return book_info
        
        # 3. Babelio (backup français)
        book_info = self.babelio.search_babelio(author, title)
        if book_info:
            logger.info(f"   ✅ Livre trouvé sur Babelio (backup)")
            return book_info
        
        logger.warning(f"   ❌ Audiobook non trouvé sur les sources disponibles")
        return None
