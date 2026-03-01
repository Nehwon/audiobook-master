#!/usr/bin/env python3
"""
Configuration du système de traitement d'audiobooks
"""

from pathlib import Path
from dataclasses import dataclass
import os
from typing import Optional

@dataclass
class ProcessingConfig:
    """Configuration principale du traitement"""
    source_directory: str = "/home/fabrice/Documents/Audiobooks"
    output_directory: str = "/home/fabrice/Documents/Audiobooks_Processed"
    temp_directory: str = "/tmp/audiobooks"
    
    # Conversion HAUTE QUALITÉ
    audio_bitrate: str = "192k"  # 192k pour stéréo haute qualité (96k par canal)
    audio_codec: str = "aac"
    audio_channels: int = 2  # Force stéréo pour effets spatiaux
    sample_rate: int = 44100  # Préserve sample rate source
    aac_coder: str = "twoloop"  # Meilleur preset AAC natif
    cutoff_freq: int = 20000  # Fréquence haute conservée pour clarté
    aac_profile: str = "aac_lc"  # Low Complexity pour compatibilité
    
    # GPU et optimisations
    enable_gpu_acceleration: bool = True
    gpu_encoder: str = "h264_nvenc"  # NVIDIA NVENC
    gpu_preset: str = "fast"
    gpu_profile: str = "high"
    gpu_level: str = "4.1"
    gpu_pix_fmt: str = "yuv420p"
    
    # Normalisation audio (EBU R128 standard pour audiobooks)
    enable_loudnorm: bool = True
    loudnorm_target: float = -16.0  # Niveau cible EBU R128
    loudnorm_range: float = 11.0  # Dynamic range préservée
    
    # Compression dynamique optionnelle
    enable_compressor: bool = True
    compressor_settings: str = "acompressor=threshold=-19dB:ratio=4:attack=5:release=100"
    
    # Chapitrage automatique
    enable_chapters: bool = True
    
    # Métadonnées
    cover_size: tuple = (600, 600)
    cover_quality: int = 85
    
    # Métadonnées
    default_language: str = "fr"
    default_genre: str = "Audiobook"
    
    # Scraping
    enable_scraping: bool = True
    scraping_sources: list = None
    
    # IA
    ollama_model: str = "llama2"
    enable_synopsis_generation: bool = True
    
    # Upload
    enable_upload: bool = False
    audiobookshelf_host: Optional[str] = None
    audiobookshelf_port: int = 13378
    audiobookshelf_username: Optional[str] = None
    audiobookshelf_password: Optional[str] = None
    
    def __post_init__(self):
        if self.scraping_sources is None:
            self.scraping_sources = ["babelio", "fnac"]
        
        # Crée les répertoires nécessaires
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        Path(self.temp_directory).mkdir(parents=True, exist_ok=True)

# Patterns de reconnaissance des noms de fichiers
FILENAME_PATTERNS = [
    # Auteur - Titre - Narrateur
    r'^([^–-]+)\s*[–-]\s*([^–-]+)\s*[–-]\s*(.+)$',
    # Auteur - Titre
    r'^([^–-]+)\s*[–-]\s*([^–-]+)$',
    # Titre - Auteur
    r'^([^–-]+)\s*[–-]\s*([^–-]+)$',
    # Série Tome X - Titre
    r'^([^–-]+)\s+(?:Tome|Volume)\s+(\d+)\s*[–-]\s*(.+)$',
    # Auteur - Série Tome X - Titre
    r'^([^–-]+)\s*[–-]\s*([^–-]+)\s+(?:Tome|Volume)\s+(\d+)\s*[–-]\s*(.+)$',
]

# Nettoyage des noms de fichiers
CLEANUP_PATTERNS = [
    (r'\[.*?\]', ''),  # Supprime les crochets
    (r'\(.*?\)', ''),  # Supprime les parenthèses
    (r'\s+', ' '),     # Multiple espaces
    (r'^\s+|\s+$', ''), # Espaces en début/fin
]

# Extensions audio supportées
AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.wav', '.flac', '.aac', '.ogg'}

# Extensions d'archive supportées
ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z'}
