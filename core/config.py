#!/usr/bin/env python3
"""
Configuration du système de traitement d'audiobooks
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List

from .runtime_paths import resolve_runtime_paths

@dataclass
class ProcessingConfig:
    """Configuration principale du traitement"""
    source_directory: str = field(default_factory=lambda: str(resolve_runtime_paths(profile="core").source))
    output_directory: str = field(default_factory=lambda: str(resolve_runtime_paths(profile="core").output))
    temp_directory: str = field(default_factory=lambda: str(resolve_runtime_paths(profile="core").temp))
    
    # Phase 1: Concaténation 1:1 Rapide (sans réencodage)
    audio_bitrate: str = "192k"  # Valeur par défaut alignée avec les tests/UX
    audio_codec: str = "copy"  # Copie directe du codec source
    audio_channels: int = 2  # Conserve les canaux originaux
    sample_rate: int = 44100  # 44.1kHz par défaut
    aac_coder: str = "fast"  # Non utilisé en phase 1
    cutoff_freq: int = 24000  # Non utilisé en phase 1
    aac_profile: str = "aac_low"  # Non utilisé en phase 1
    
    # Mode de traitement
    processing_mode: str = "encode_aac"  # "concat_fast" | "encode_aac" | "final_m4b"
    
    # GPU et optimisations (pour compatibilité)
    enable_gpu_acceleration: bool = True
    enable_aac_optimization: bool = True
    aac_low_latency: bool = False  # Désactivé pour meilleure compression
    aac_vbr: bool = False  # CBR pour taille prévisible (plus petit que VBR)
    
    # Paramètres avancés (interface)
    enable_vbr: bool = False  # VBR optionnel (décoché par défaut)
    vbr_quality: int = 5  # Qualité VBR (1-9)
    
    # Loudnorm avancé (modifiable interface)
    enable_loudnorm: bool = True
    loudnorm_target: float = -18.0  # Integrated Loudness (-23 à -14 LUFS)
    loudnorm_range: float = 11.0  # Loudness Range (4-20 LU)
    loudnorm_true_peak: float = -1.5  # True Peak (-3 à -1 dBTP)
    
    # Bitrates disponibles
    available_bitrates: List[str] = field(default_factory=lambda: ["64k", "96k", "128k", "160k", "192k", "256k", "320k"])
    default_bitrate: str = "192k"
    
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
    audiobookshelf_token: Optional[str] = None
    audiobookshelf_library_id: Optional[str] = None
    
    def __post_init__(self):
        # Surcharge optionnelle via variables d'environnement
        self.audiobookshelf_host = os.getenv("AUDIOBOOKSHELF_HOST", self.audiobookshelf_host)

        port_value = os.getenv("AUDIOBOOKSHELF_PORT")
        if port_value:
            try:
                self.audiobookshelf_port = int(port_value)
            except ValueError:
                pass

        self.audiobookshelf_username = os.getenv("AUDIOBOOKSHELF_USERNAME", self.audiobookshelf_username)
        self.audiobookshelf_password = os.getenv("AUDIOBOOKSHELF_PASSWORD", self.audiobookshelf_password)
        self.audiobookshelf_token = os.getenv("AUDIOBOOKSHELF_TOKEN", self.audiobookshelf_token)
        self.audiobookshelf_library_id = os.getenv("AUDIOBOOKSHELF_LIBRARY_ID", self.audiobookshelf_library_id)

        if self.scraping_sources is None:
            self.scraping_sources = ["babelio", "fnac"]
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
