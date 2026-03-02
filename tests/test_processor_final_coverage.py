"""
Tests étendus pour core/processor.py - Focus sur le coverage des fonctions existantes
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import time
from pathlib import Path

from core.processor import AudiobookProcessor, AudiobookMetadata
from core.config import ProcessingConfig


class TestProcessorFinalCoverage(unittest.TestCase):
    """Tests étendus pour couvrir les fonctions existantes de processor.py"""

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

    def test_convert_to_m4b_with_metadata(self):
        """Test la conversion avec métadonnées"""
        config = ProcessingConfig()
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_subprocess_error(self):
        """Test la gestion des erreurs subprocess"""
        config = ProcessingConfig()
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"Error message")
            mock_process.returncode = 1
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertFalse(result)

    def test_convert_to_m4b_subprocess_exception(self):
        """Test la gestion des exceptions subprocess"""
        config = ProcessingConfig()
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_popen.side_effect = Exception("Subprocess error")
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertFalse(result)

    def test_convert_to_m4b_timeout_handling(self):
        """Test la gestion du timeout"""
        config = ProcessingConfig()
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.side_effect = Exception("Timeout")
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertFalse(result)

    def test_convert_to_m4b_multiple_files(self):
        """Test la conversion avec plusieurs fichiers audio"""
        config = ProcessingConfig()
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [
                self.source_dir / "audio1.mp3",
                self.source_dir / "audio2.mp3",
                self.source_dir / "audio3.mp3"
            ]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_high_quality(self):
        """Test la conversion haute qualité"""
        config = ProcessingConfig()
        config.audio_bitrate = "256k"
        config.audio_channels = 2
        config.cutoff_freq = 20000
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_with_chapters(self):
        """Test la conversion avec chapitres activés"""
        config = ProcessingConfig()
        config.enable_chapters = True
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_without_chapters(self):
        """Test la conversion sans chapitres"""
        config = ProcessingConfig()
        config.enable_chapters = False
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_with_loudnorm(self):
        """Test la conversion avec normalisation audio"""
        config = ProcessingConfig()
        config.enable_loudnorm = True
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_with_compression(self):
        """Test la conversion avec compression"""
        config = ProcessingConfig()
        config.enable_compressor = True
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_gpu_acceleration(self):
        """Test la conversion avec accélération GPU"""
        config = ProcessingConfig()
        config.enable_gpu_acceleration = True
        config.gpu_encoder = "h264_nvenc"
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_fdk_aac(self):
        """Test la conversion avec FDK-AAC"""
        config = ProcessingConfig()
        config.aac_coder = "twolo"
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_convert_to_m4b_custom_sample_rate(self):
        """Test la conversion avec sample rate personnalisé"""
        config = ProcessingConfig()
        config.sample_rate = 48000
        config.audio_bitrate = "128k"
        self.processor.config = config
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            audio_files = [self.source_dir / "audio1.mp3"]
            output_file = self.output_dir / "output.m4b"
            metadata = AudiobookMetadata(title="Test", author="Author")
            
            result = self.processor.convert_to_m4b(audio_files, output_file, metadata)
            
            self.assertTrue(result)
            mock_popen.assert_called_once()

    def test_generate_synopsis_success(self):
        """Test la génération de synopsis réussie"""
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author",
            description="Test description"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Generated synopsis"
            
            result = self.processor.generate_synopsis(metadata)
            
            self.assertEqual(result, "Generated synopsis")

    def test_generate_synopsis_failure(self):
        """Test l'échec de génération de synopsis"""
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Ollama error")
            
            result = self.processor.generate_synopsis(metadata)
            
            self.assertIsNone(result)

    def test_generate_synopsis_disabled(self):
        """Test la génération de synopsis désactivée"""
        config = ProcessingConfig()
        config.enable_synopsis_generation = False
        self.processor.config = config
        
        metadata = AudiobookMetadata(
            title="Test Book",
            author="Test Author"
        )
        
        result = self.processor.generate_synopsis(metadata)
        
        self.assertIsNone(result)

    def test_scrap_book_info_disabled(self):
        """Test le scraping désactivé"""
        config = ProcessingConfig()
        config.enable_scraping = False
        self.processor.config = config
        
        result = self.processor.scrap_book_info("Test Author", "Test Book")
        
        self.assertIsNone(result)

    def test_scrap_book_info_success(self):
        """Test le scraping réussi"""
        config = ProcessingConfig()
        config.enable_scraping = True
        self.processor.config = config
        
        with patch.object(self.processor, 'scrap_audible') as mock_audible:
            mock_audible.return_value = AudiobookMetadata(
                title="Test Book",
                author="Test Author"
            )
            
            result = self.processor.scrap_book_info("Test Author", "Test Book")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.title, "Test Book")

    def test_scrap_book_info_fallback(self):
        """Test le scraping avec fallback"""
        config = ProcessingConfig()
        config.enable_scraping = True
        self.processor.config = config
        
        with patch.object(self.processor, 'scrap_audible') as mock_audible:
            with patch.object(self.processor, 'scrap_babelio') as mock_babelio:
                mock_audible.return_value = None
                mock_babelio.return_value = AudiobookMetadata(
                    title="Test Book",
                    author="Test Author"
                )
                
                result = self.processor.scrap_book_info("Test Author", "Test Book")
                
                self.assertIsNotNone(result)
                self.assertEqual(result.title, "Test Book")

    def test_scrap_book_info_no_results(self):
        """Test le scraping sans résultats"""
        config = ProcessingConfig()
        config.enable_scraping = True
        self.processor.config = config
        
        with patch.object(self.processor, 'scrap_audible') as mock_audible:
            with patch.object(self.processor, 'scrap_babelio') as mock_babelio:
                mock_audible.return_value = None
                mock_babelio.return_value = None
                
                result = self.processor.scrap_book_info("Test Author", "Test Book")
                
                self.assertIsNone(result)

    def test_download_cover_success(self):
        """Test le téléchargement de pochette réussi"""
        cover_url = "http://example.com/cover.jpg"
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = b"fake image content"
            mock_get.return_value = mock_response
            
            result = self.processor.download_cover(cover_url)
            
            self.assertIsNotNone(result)

    def test_download_cover_failure(self):
        """Test l'échec de téléchargement de pochette"""
        cover_url = "http://example.com/cover.jpg"
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Download error")
            
            result = self.processor.download_cover(cover_url)
            
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
