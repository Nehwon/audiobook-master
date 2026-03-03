"""
Tests ciblés pour core/processor.py - Focus sur les fonctions manquantes pour atteindre 70%
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path

from core.processor import AudiobookProcessor, AudiobookMetadata
from core.config import ProcessingConfig


class TestProcessorTargetedCoverage(unittest.TestCase):
    """Tests ciblés pour couvrir les fonctions manquantes de processor.py et atteindre 70%"""

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

    def test_parse_filename_with_author_title(self):
        """Test le parsing de nom de fichier avec auteur et titre"""
        filename = "Author - Title.mp3"
        
        result = self.processor.parse_filename(filename)
        
        self.assertEqual(result.title, "Title")
        self.assertEqual(result.author, "Author")

    def test_parse_filename_with_title_only(self):
        """Test le parsing de nom de fichier avec titre seul"""
        filename = "Title Only.mp3"
        
        result = self.processor.parse_filename(filename)
        
        self.assertEqual(result.title, "Title Only")
        self.assertIsNone(result.author)

    def test_parse_filename_with_dashes(self):
        """Test le parsing de nom de fichier avec tirets multiples"""
        filename = "Author - Title - Subtitle.mp3"
        
        result = self.processor.parse_filename(filename)
        
        self.assertEqual(result.title, "Title - Subtitle")
        self.assertEqual(result.author, "Author")

    def test_parse_filename_with_numbers(self):
        """Test le parsing de nom de fichier avec nombres"""
        filename = "Author - Title 2.mp3"
        
        result = self.processor.parse_filename(filename)
        
        self.assertEqual(result.title, "Title 2")
        self.assertEqual(result.author, "Author")

    def test_parse_filename_empty(self):
        """Test le parsing de nom de fichier vide"""
        filename = ""
        
        result = self.processor.parse_filename(filename)
        
        self.assertIsNone(result)

    def test_parse_filename_no_extension(self):
        """Test le parsing de nom de fichier sans extension"""
        filename = "Author - Title"
        
        result = self.processor.parse_filename(filename)
        
        self.assertEqual(result.title, "Title")
        self.assertEqual(result.author, "Author")

    def test_validate_metadata_complete(self):
        """Test la validation de métadonnées complètes"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            narrator="Test Narrator",
            publisher="Test Publisher",
            publication_date="2023",
            isbn="1234567890",
            language="fr",
            description="Test Description",
            cover_url="http://example.com/cover.jpg",
            rating=4.5,
            genres=["Fiction"],
            series="Test Series",
            series_number="1",
            duration="10h30m",
            asin="B123456789"
        )
        
        result = self.processor.validate_metadata(metadata)
        
        self.assertTrue(result)

    def test_validate_metadata_missing_required(self):
        """Test la validation avec métadonnées requises manquantes"""
        metadata = AudiobookMetadata(
            title="",  # Titre vide
            author="Test Author"
        )
        
        result = self.processor.validate_metadata(metadata)
        
        self.assertFalse(result)

    def test_validate_metadata_missing_author(self):
        """Test la validation avec auteur manquant"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author=""  # Auteur vide
        )
        
        result = self.processor.validate_metadata(metadata)
        
        self.assertFalse(result)

    def test_validate_metadata_minimal_valid(self):
        """Test la validation avec métadonnées minimales valides"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author"
        )
        
        result = self.processor.validate_metadata(metadata)
        
        self.assertTrue(result)

    def test_validate_metadata_invalid_rating(self):
        """Test la validation avec note invalide"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            rating=6.0  # Note invalide (> 5)
        )
        
        result = self.processor.validate_metadata(metadata)
        
        self.assertFalse(result)

    def test_validate_metadata_negative_rating(self):
        """Test la validation avec note négative"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            rating=-1.0  # Note négative
        )
        
        result = self.processor.validate_metadata(metadata)
        
        self.assertFalse(result)

    def test_validate_metadata_invalid_language(self):
        """Test la validation avec langue invalide"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            language="invalid"  # Langue invalide
        )
        
        result = self.processor.validate_metadata(metadata)
        
        self.assertFalse(result)

    def test_create_output_directory_success(self):
        """Test la création de répertoire de sortie réussie"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author"
        )
        
        result = self.processor.create_output_directory(metadata)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.exists())

    def test_create_output_directory_with_special_chars(self):
        """Test la création de répertoire avec caractères spéciaux"""
        metadata = AudiobookMetadata(
            title="Test/Title:Special*Chars",
            author="Test/Author"
        )
        
        result = self.processor.create_output_directory(metadata)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.exists())

    def test_create_output_directory_nested(self):
        """Test la création de répertoire imbriqué"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            series="Test Series",
            series_number="1"
        )
        
        result = self.processor.create_output_directory(metadata)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.exists())

    def test_create_output_directory_permission_error(self):
        """Test la création de répertoire avec erreur de permissions"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author"
        )
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Permission denied")
            
            result = self.processor.create_output_directory(metadata)
            
            self.assertIsNone(result)

    def test_generate_chapters_from_metadata(self):
        """Test la génération de chapitres depuis métadonnées"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            chapters=[
                {"title": "Chapter 1", "start": "00:00:00", "end": "00:30:00"},
                {"title": "Chapter 2", "start": "00:30:00", "end": "01:00:00"}
            ]
        )
        
        result = self.processor.generate_chapters(metadata)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Chapter 1")
        self.assertEqual(result[0]["start"], "00:00:00")
        self.assertEqual(result[0]["end"], "00:30:00")

    def test_generate_chapters_without_metadata(self):
        """Test la génération de chapitres sans métadonnées"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author"
        )
        
        result = self.processor.generate_chapters(metadata)
        
        self.assertEqual(result, [])

    def test_generate_chapters_empty_chapters(self):
        """Test la génération de chapitres avec liste vide"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            chapters=[]
        )
        
        result = self.processor.generate_chapters(metadata)
        
        self.assertEqual(result, [])

    def test_generate_chapters_invalid_format(self):
        """Test la génération de chapitres avec format invalide"""
        metadata = AudiobookMetadata(
            title="Test Title",
            author="Test Author",
            chapters=[
                {"title": "Chapter 1"},  # Manque start/end
                {"title": "Chapter 2", "start": "00:30:00"}  # Manque end
            ]
        )
        
        result = self.processor.generate_chapters(metadata)
        
        self.assertEqual(result, [])

    def test_cleanup_temp_files_success(self):
        """Test le nettoyage des fichiers temporaires réussi"""
        # Créer des fichiers temporaires
        temp_file1 = self.temp_dir_path / "temp1.mp3"
        temp_file2 = self.temp_dir_path / "temp2.m4b"
        temp_file1.write_bytes(b"temp content")
        temp_file2.write_bytes(b"temp content")
        
        result = self.processor.cleanup_temp_files()
        
        self.assertTrue(result)
        self.assertFalse(temp_file1.exists())
        self.assertFalse(temp_file2.exists())

    def test_cleanup_temp_files_empty_directory(self):
        """Test le nettoyage de répertoire temporaire vide"""
        result = self.processor.cleanup_temp_files()
        
        self.assertTrue(result)

    def test_cleanup_temp_files_permission_error(self):
        """Test le nettoyage avec erreur de permissions"""
        with patch('pathlib.Path.unlink') as mock_unlink:
            mock_unlink.side_effect = PermissionError("Permission denied")
            
            result = self.processor.cleanup_temp_files()
            
            self.assertFalse(result)

    def test_get_audio_duration_success(self):
        """Test l'obtention de la durée audio réussie"""
        audio_file = self.source_dir / "test.mp3"
        audio_file.write_bytes(b"fake audio content")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "00:10:30"
            
            result = self.processor.get_audio_duration(audio_file)
            
            self.assertEqual(result, "00:10:30")

    def test_get_audio_duration_ffmpeg_error(self):
        """Test l'obtention de la durée avec erreur FFmpeg"""
        audio_file = self.source_dir / "test.mp3"
        audio_file.write_bytes(b"fake audio content")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "FFmpeg error"
            
            result = self.processor.get_audio_duration(audio_file)
            
            self.assertIsNone(result)

    def test_get_audio_duration_file_not_found(self):
        """Test l'obtention de la durée avec fichier inexistant"""
        audio_file = self.source_dir / "nonexistent.mp3"
        
        result = self.processor.get_audio_duration(audio_file)
        
        self.assertIsNone(result)

    def test_get_audio_duration_subprocess_exception(self):
        """Test l'obtention de la durée avec exception subprocess"""
        audio_file = self.source_dir / "test.mp3"
        audio_file.write_bytes(b"fake audio content")
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Subprocess error")
            
            result = self.processor.get_audio_duration(audio_file)
            
            self.assertIsNone(result)

    def test_check_audio_format_valid_mp3(self):
        """Test la vérification de format audio MP3 valide"""
        audio_file = self.source_dir / "test.mp3"
        audio_file.write_bytes(b"fake audio content")
        
        result = self.processor.check_audio_format(audio_file)
        
        self.assertTrue(result)

    def test_check_audio_format_valid_m4a(self):
        """Test la vérification de format audio M4A valide"""
        audio_file = self.source_dir / "test.m4a"
        audio_file.write_bytes(b"fake audio content")
        
        result = self.processor.check_audio_format(audio_file)
        
        self.assertTrue(result)

    def test_check_audio_format_invalid_format(self):
        """Test la vérification de format audio invalide"""
        audio_file = self.source_dir / "test.txt"
        audio_file.write_bytes(b"not audio")
        
        result = self.processor.check_audio_format(audio_file)
        
        self.assertFalse(result)

    def test_check_audio_format_file_not_found(self):
        """Test la vérification de format avec fichier inexistant"""
        audio_file = self.source_dir / "nonexistent.mp3"
        
        result = self.processor.check_audio_format(audio_file)
        
        self.assertFalse(result)

    def test_merge_metadata_success(self):
        """Test la fusion de métadonnées réussie"""
        base_metadata = AudiobookMetadata(
            title="Base Title",
            author="Base Author"
        )
        
        new_metadata = AudiobookMetadata(
            title="New Title",
            narrator="New Narrator",
            publisher="New Publisher"
        )
        
        result = self.processor.merge_metadata(base_metadata, new_metadata)
        
        # Conserve les champs de base
        self.assertEqual(result.author, "Base Author")
        # Ajoute les nouveaux champs
        self.assertEqual(result.narrator, "New Narrator")
        self.assertEqual(result.publisher, "New Publisher")

    def test_merge_metadata_empty_new(self):
        """Test la fusion avec métadonnées nouvelles vides"""
        base_metadata = AudiobookMetadata(
            title="Base Title",
            author="Base Author"
        )
        
        new_metadata = AudiobookMetadata()
        
        result = self.processor.merge_metadata(base_metadata, new_metadata)
        
        self.assertEqual(result.title, "Base Title")
        self.assertEqual(result.author, "Base Author")

    def test_merge_metadata_empty_base(self):
        """Test la fusion avec métadonnées de base vides"""
        base_metadata = AudiobookMetadata()
        
        new_metadata = AudiobookMetadata(
            title="New Title",
            author="New Author"
        )
        
        result = self.processor.merge_metadata(base_metadata, new_metadata)
        
        self.assertEqual(result.title, "New Title")
        self.assertEqual(result.author, "New Author")


if __name__ == '__main__':
    unittest.main()
