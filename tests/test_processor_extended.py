"""
Tests unitaires supplémentaires pour core/processor.py
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import time
from pathlib import Path

from core.processor import AudiobookProcessor, AudiobookMetadata
from core.config import ProcessingConfig


class TestAudiobookProcessorExtended(unittest.TestCase):
    """Tests étendus pour la classe AudiobookProcessor"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.output_dir = Path(self.temp_dir) / "output"
        self.temp_dir_path = Path(self.temp_dir) / "temp"

        self.source_dir.mkdir()
        self.output_dir.mkdir()
        self.temp_dir_path.mkdir()

        self.processor = AudiobookProcessor(
            str(self.source_dir),
            str(self.output_dir),
            str(self.temp_dir_path)
        )
        self.processor.config = ProcessingConfig()

    def test_normalize_filename(self):
        """Test la normalisation des noms de fichiers"""
        # Test avec accents et caractères spéciaux
        filename = "Téte-à-Tête & Co! (2023).mp3"
        normalized = self.processor.normalize_filename(filename)
        
        self.assertNotIn("é", normalized)
        self.assertNotIn("&", normalized)
        self.assertNotIn("!", normalized)
        self.assertNotIn("(", normalized)
        self.assertNotIn(")", normalized)
        self.assertIn("Tete-a-Tete", normalized)
        self.assertIn("2023", normalized)

    def test_normalize_filename_multiple_spaces(self):
        """Test la normalisation des espaces multiples"""
        filename = "Auteur   -    Titre     .mp3"
        normalized = self.processor.normalize_filename(filename)
        
        self.assertNotIn("   ", normalized)
        self.assertNotIn("    ", normalized)
        self.assertEqual(normalized, "Auteur - Titre.mp3")

    def test_parse_filename_simple(self):
        """Test le parsing simple: Auteur - Titre"""
        metadata = self.processor.parse_filename("Stephen King - Ca.mp3")
        
        self.assertEqual(metadata.author, "Stephen King")
        self.assertEqual(metadata.title, "Ca")
        self.assertEqual(metadata.genre, "Audiobook")
        self.assertEqual(metadata.language, "fr")

    def test_parse_filename_with_series(self):
        """Test le parsing avec série: Auteur - Série - Tome X - Titre"""
        metadata = self.processor.parse_filename("J.K. Rowling - Harry Potter - Tome 1 - Harry Potter à l'école des sorciers.zip")
        
        self.assertEqual(metadata.author, "J.K. Rowling")
        self.assertEqual(metadata.title, "J.K. Rowling - Harry Potter - Tome 1 - Harry Potter à l'école des sorciers")
        self.assertEqual(metadata.short_title, "Harry Potter à l'école des sorciers")
        self.assertEqual(metadata.series, "Harry Potter")
        self.assertEqual(metadata.series_number, "1")

    def test_parse_filename_with_narrator(self):
        """Test le parsing avec narrateur: Auteur - Titre (lu par Narrateur)"""
        metadata = self.processor.parse_filename("George Orwell - 1984 (lu par Bernard Giraudeau).m4a")
        
        self.assertEqual(metadata.author, "George Orwell")
        self.assertEqual(metadata.title, "1984")
        self.assertEqual(metadata.narrator, "Bernard Giraudeau")

    def test_parse_filename_fallback(self):
        """Test le fallback pour noms de fichiers non reconnus"""
        metadata = self.processor.parse_filename("fichier_inconnu.zip")
        
        self.assertEqual(metadata.author, "Inconnu")
        self.assertEqual(metadata.title, "fichier_inconnu")
        self.assertEqual(metadata.genre, "Audiobook")

    def test_extract_archive_zip(self):
        """Test l'extraction d'archive ZIP"""
        # Crée un faux fichier ZIP
        zip_path = self.source_dir / "test.zip"
        zip_path.write_bytes(b"fake zip content")
        
        extract_to = Path(self.temp_dir) / "extract"
        extract_to.mkdir()
        
        # Mock zipfile.ZipFile
        with patch('zipfile.ZipFile') as mock_zip:
            mock_zip.return_value.__enter__.return_value = None
            
            result = self.processor.extract_archive(zip_path, extract_to)
            
            self.assertTrue(result)
            mock_zip.assert_called_once_with(zip_path, 'r')

    def test_extract_archive_rar(self):
        """Test l'extraction d'archive RAR"""
        # Crée un faux fichier RAR
        rar_path = self.source_dir / "test.rar"
        rar_path.write_bytes(b"fake rar content")
        
        extract_to = Path(self.temp_dir) / "extract"
        extract_to.mkdir()
        
        # Mock rarfile.RarFile
        with patch('rarfile.RarFile') as mock_rar:
            mock_rar.return_value.__enter__.return_value = None
            
            result = self.processor.extract_archive(rar_path, extract_to)
            
            self.assertTrue(result)
            mock_rar.assert_called_once_with(rar_path, 'r')

    def test_extract_archive_unsupported(self):
        """Test l'extraction d'archive non supportée"""
        # Crée un fichier avec extension non supportée
        unsupported_path = self.source_dir / "test.7z"
        unsupported_path.write_bytes(b"fake content")
        
        extract_to = Path(self.temp_dir) / "extract"
        extract_to.mkdir()
        
        result = self.processor.extract_archive(unsupported_path, extract_to)
        
        self.assertFalse(result)

    def test_find_audio_files(self):
        """Test la recherche de fichiers audio"""
        # Crée des fichiers de test
        (self.source_dir / "file1.mp3").write_bytes(b"audio1")
        (self.source_dir / "file2.m4a").write_bytes(b"audio2")
        (self.source_dir / "file3.txt").write_bytes(b"text")
        
        # Crée un sous-dossier avec des fichiers audio
        subdir = self.source_dir / "subdir"
        subdir.mkdir()
        (subdir / "file4.wav").write_bytes(b"audio3")
        
        audio_files = self.processor.find_audio_files(self.source_dir)
        
        self.assertEqual(len(audio_files), 3)
        extensions = [f.suffix for f in audio_files]
        self.assertIn('.mp3', extensions)
        self.assertIn('.m4a', extensions)
        self.assertIn('.wav', extensions)
        self.assertNotIn('.txt', extensions)

    def test_check_fdk_aac_available(self):
        """Test la détection du codec FDK-AAC disponible"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "libfdk_aac"
            mock_run.return_value.returncode = 0
            
            result = self.processor.check_fdk_aac()
            
            self.assertTrue(result)
            mock_run.assert_called_once_with(['ffmpeg', '-hide_banner', '-encoders'], 
                                          capture_output=True, text=True, timeout=5)

    def test_check_fdk_aac_unavailable(self):
        """Test la détection du codec FDK-AAC non disponible"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "aac"
            mock_run.return_value.returncode = 0
            
            result = self.processor.check_fdk_aac()
            
            self.assertFalse(result)

    def test_detect_gpu_acceleration_success(self):
        """Test la détection GPU réussie"""
        with patch('subprocess.run') as mock_run:
            # Mock ffmpeg avec NVENC
            mock_run.side_effect = [
                MagicMock(stdout="h264_nvenc", returncode=0),  # ffmpeg encoders
                MagicMock(stdout="NVIDIA RTX 4070", returncode=0)  # nvidia-smi
            ]
            
            result = self.processor.detect_gpu_acceleration()
            
            self.assertTrue(result)
            self.assertEqual(mock_run.call_count, 2)

    def test_detect_gpu_acceleration_no_nvenc(self):
        """Test la détection GPU sans NVENC"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "aac"
            mock_run.return_value.returncode = 0
            
            result = self.processor.detect_gpu_acceleration()
            
            self.assertFalse(result)

    def test_add_cover_to_m4b_success(self):
        """Test l'ajout de pochette réussi"""
        # Crée des fichiers de test
        m4b_path = self.output_dir / "test.m4b"
        m4b_path.write_bytes(b"fake m4b content")
        
        cover_path = self.source_dir / "cover.jpg"
        cover_path.write_bytes(b"fake cover content")
        
        # Mock PIL et mutagen
        with patch('PIL.Image.open') as mock_image:
            with patch('mutagen.mp4.MP4') as mock_mp4:
                # Configuration des mocks
                mock_img = MagicMock()
                mock_img.convert.return_value = mock_img
                mock_img.resize.return_value = mock_img
                mock_image.return_value.__enter__.return_value = mock_img
                
                mock_audio = MagicMock()
                mock_mp4.return_value = mock_audio
                
                result = self.processor.add_cover_to_m4b(m4b_path, str(cover_path))
                
                self.assertTrue(result)
                mock_audio.save.assert_called_once()

    def test_add_cover_to_m4b_failure(self):
        """Test l'ajout de pochette échoué"""
        # Crée des fichiers de test
        m4b_path = self.output_dir / "test.m4b"
        m4b_path.write_bytes(b"fake m4b content")
        
        cover_path = self.source_dir / "cover.jpg"
        cover_path.write_bytes(b"fake cover content")
        
        # Mock PIL avec erreur
        with patch('PIL.Image.open', side_effect=Exception("Image error")):
            result = self.processor.add_cover_to_m4b(m4b_path, str(cover_path))
            
            self.assertFalse(result)

    def test_scrap_book_info_success(self):
        """Test le scraping d'informations réussi"""
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author"
        )
        
        with patch('core.processor.BookScraper') as mock_scraper:
            mock_scraper_instance = MagicMock()
            mock_scraper.return_value = mock_scraper_instance
            
            # Mock BookInfo
            mock_book_info = MagicMock()
            mock_book_info.publisher = "Test Publisher"
            mock_book_info.publication_date = "2023"
            mock_book_info.description = "Test description"
            mock_book_info.cover_url = "http://example.com/cover.jpg"
            mock_book_info.genres = ["Fiction", "Thriller"]
            mock_book_info.series = "Test Series"
            mock_book_info.rating = 4.5
            
            mock_scraper_instance.search_book.return_value = mock_book_info
            mock_scraper_instance.babelio.download_cover.return_value = True
            
            result = self.processor.scrap_book_info(metadata)
            
            self.assertEqual(result.publisher, "Test Publisher")
            self.assertEqual(result.year, "2023")
            self.assertEqual(result.description, "Test description")
            self.assertEqual(result.genre, "Fiction, Thriller")
            self.assertEqual(result.series, "Test Series")

    def test_generate_synopsis_success(self):
        """Test la génération de synopsis réussie"""
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Generated synopsis content"
            
            result = self.processor.generate_synopsis(metadata)
            
            self.assertEqual(result, "Generated synopsis content")
            mock_run.assert_called_once()

    def test_generate_synopsis_failure(self):
        """Test la génération de synopsis échouée"""
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Error"
            
            result = self.processor.generate_synopsis(metadata)
            
            # Fallback vers synopsis par défaut
            self.assertIn("Test Book", result)
            self.assertIn("Test Author", result)

    def test_download_cover_existing(self):
        """Test le téléchargement de pochette existante"""
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author",
            cover_path="/existing/cover.jpg"
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            result = self.processor.download_cover(metadata)
            
            self.assertEqual(result, "/existing/cover.jpg")

    def test_download_cover_missing(self):
        """Test le téléchargement de pochette manquant"""
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author"
        )
        
        result = self.processor.download_cover(metadata)
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
