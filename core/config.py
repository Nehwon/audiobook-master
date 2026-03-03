#!/usr/bin/env python3
"""
Configuration du système de traitement d'audiobooks
"""

from pathlib import Path
from dataclasses import dataclass
import os
import weakref
from typing import Optional

@dataclass
class ProcessingConfig:
    """Configuration principale du traitement"""
    source_directory: str = "/home/fabrice/Documents/Audiobooks"
    output_directory: str = "/home/fabrice/Documents/Projets/scripts_audiobooks/test_audio"
    temp_directory: str = "/tmp/audiobooks"
    
    # Phase 1: Concaténation 1:1 Rapide (sans réencodage)
    audio_bitrate: str = "copy"  # COPY = pas de réencodage, vitesse maximale
    audio_codec: str = "copy"  # Copie directe du codec source
    audio_channels: int = 2  # Conserve les canaux originaux
    sample_rate: int = 48000  # 48kHz haute qualité (conservé si possible)
    aac_coder: str = "fast"  # Non utilisé en phase 1
    cutoff_freq: int = 24000  # Non utilisé en phase 1
    aac_profile: str = "aac_low"  # Non utilisé en phase 1
    
    # Mode de traitement
    processing_mode: str = "concat_fast"  # "concat_fast" | "encode_aac" | "final_m4b"
    
    # GPU et optimisations (pour compatibilité)
    enable_gpu_acceleration: bool = True
    enable_aac_optimization: bool = True
    aac_low_latency: bool = False  # Désactivé pour meilleure compression
    aac_vbr: bool = False  # CBR pour taille prévisible (plus petit que VBR)
    
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
    
    # Scraping DÉSACTIVÉ pour vitesse maximale
    enable_scraping: bool = False
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
        # Purge des références faibles (si disponible)
        try:
            weakref.collect()
        except AttributeError:
            pass  # weakref.collect n'existe pas dans toutes les versions
        # Crée les répertoires nécessaires
        Path(self.source_directory).mkdir(parents=True, exist_ok=True)
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
