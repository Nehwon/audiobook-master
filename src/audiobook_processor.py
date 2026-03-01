#!/usr/bin/env python3
"""
Système complet de traitement d'audiobooks
- Renommage automatique
- Conversion M4B
- Métadonnées
- Synopsis IA
- Pochettes
- Upload Audiobookshelf
"""

import os
import re
import json
import shutil
import subprocess
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import quote
import logging
import unicodedata
from bs4 import BeautifulSoup
import tempfile
from PIL import Image
import mutagen
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB
import zipfile
import rarfile
from config import ProcessingConfig

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AudiobookMetadata:
    """Métadonnées complètes d'un audiobook"""
    # Identification principale
    title: str
    author: str
    short_title: Optional[str] = None  # Titre court (sans série)
    narrator: Optional[str] = None
    series: Optional[str] = None
    series_number: Optional[str] = None
    
    # Métadonnées avancées
    year: Optional[str] = None
    genre: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    asin: Optional[str] = None
    language: str = "fr"
    
    # Métadonnées techniques
    total_tracks: Optional[int] = None
    disc_number: Optional[int] = None
    total_discs: Optional[int] = None
    
    # Médias
    cover_path: Optional[str] = None
    
    # Chapitres (M4B)
    chapters: Optional[List[Dict]] = None
    
    def get_filename_format(self) -> str:
        """Génère le nom de fichier selon les conventions"""
        if self.series and self.series_number:
            # Format: Auteur - Série - Tome X - Titre
            return f"{self.author} - {self.series} - Tome {self.series_number} - {self.title}"
        else:
            # Format: Auteur - Titre
            return f"{self.author} - {self.title}"
    
    def get_metadata_dict(self) -> Dict[str, str]:
        """Retourne les métadonnées au format FFmpeg"""
        metadata = {
            # Métadonnées principales
            'title': self.title,
            'artist': self.narrator or self.author,  # Narrateur en priorité
            'albumartist': self.author,  # Auteur comme artiste de l'album
            'album': self.series or self.title,  # Série si disponible, sinon titre
            'genre': self.genre or "Audiobook",
            'date': self.year or "",
            
            # Métadonnées techniques
            'encodedby': "FFmpeg audiobook optimized",
            'comment': self.description or "",
            
            # Métadonnées Apple Books compatibles
            '©narr': self.narrator or "",
            '©gen': self.genre or "Audiobook",
            '©day': self.year or "",
            
            # Métadonnées étendues
            'publisher': self.publisher or "",
            'language': self.language,
            'description': self.description or "",
        }
        
        # Métadonnées de série si disponibles
        if self.series:
            metadata['series'] = self.series
            if self.series_number:
                metadata['seriespart'] = self.series_number
                metadata['track'] = f"{self.series_number}"
                if self.total_tracks:
                    metadata['totaltracks'] = str(self.total_tracks)
        
        # Métadonnées multi-disques si disponibles
        if self.disc_number:
            metadata['disc'] = str(self.disc_number)
            if self.total_discs:
                metadata['totaldiscs'] = str(self.total_discs)
        
        # ASIN si disponible
        if self.asin:
            metadata['ASIN'] = self.asin
        
        # Filtrer les valeurs vides
        return {k: v for k, v in metadata.items() if v}

class AudiobookProcessor:
    def __init__(self, source_dir: str, output_dir: str, temp_dir: str = "/tmp/audiobooks"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
    def normalize_filename(self, filename: str) -> str:
        """Normalise un nom de fichier"""
        # Supprime les accents
        filename = unicodedata.normalize('NFKD', filename)
        filename = ''.join(c for c in filename if not unicodedata.combining(c))
        
        # Remplace les caractères problématiques
        filename = re.sub(r'[^\w\s\-_.]', '', filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename
    
    def parse_filename(self, filename: str) -> AudiobookMetadata:
        """Extrait les métadonnées de base du nom de fichier avec patterns améliorés"""
        # Nettoyage initial
        filename_clean = re.sub(r'\.(zip|rar|mp3|m4a|m4b)$', '', filename)
        filename_clean = filename_clean.replace('_', ' ')
        
        # Supprime les informations techniques entre crochets/parenthèses
        filename_clean = re.sub(r'\[.*?\]', '', filename_clean)
        filename_clean = re.sub(r'\([^)]*\)', '', filename_clean)
        filename_clean = re.sub(r'\s+', ' ', filename_clean).strip()
        
        logger.info(f"🔍 Analyse du nom: {filename_clean}")
        
        # Pattern 1: Auteur - Série - Vol X - Titre (prioritaire)
        series_patterns = [
            r'(.+?)\s*[-]\s*(.+?)\s+(\d+)\s*[-:]\s*(.+)',  # Auteur - Série - Vol X - Titre
            r'(.+?)\s+(?:tome|volume|part)\s+(\d+)\s*[-:]\s*(.+)',  # Tome 1, Volume 2, Part 3
            r'(.+?)\s+(?:vol|volume)\s+(\d+)',      # Vol 1, Vol 2
            r'(.+?)\s+book\s+(\d+)',               # Book 1, Book 2
            r'(.+?)\s+(\d+)\s*[-:]\s*(.+)',   # Auteur 1 - Titre (série implicite)
        ]
        
        # Test d'abord les patterns de séries
        for pattern in series_patterns:
            series_match = re.search(pattern, filename_clean, re.IGNORECASE)
            if series_match:
                series_found = True
                author = self.normalize_filename(series_match.group(1)).strip()
                
                # Pattern Auteur - Série - Vol X - Titre
                if pattern == r'(.+?)\s*[-]\s*(.+?)\s+(\d+)\s*[-:]\s*(.+)' and len(series_match.groups()) >= 4:
                    series = self.normalize_filename(series_match.group(2)).strip()
                    series_number = series_match.group(3)
                    title = series_match.group(4).strip()
                else:
                    # Pour les autres patterns, utilise la logique standard
                    series = self.normalize_filename(series_match.group(2)).strip() if len(series_match.groups()) > 2 else ""
                    series_number = series_match.group(3) if len(series_match.groups()) > 2 else series_match.group(2)
                    title = filename_clean.replace(series_match.group(0), '').strip(' -')
                
                # Format standard : Auteur - Série - Vol X - Titre
                if "vol" in pattern.lower():
                    volume_text = f"Vol {series_number}"
                else:
                    volume_text = f"Tome {series_number}"
                
                # Reconstruit le titre complet
                if series:
                    full_title = f"{author} - {series} - {volume_text} - {title}"
                else:
                    full_title = f"{author} - {volume_text} - {title}"
                
                metadata = AudiobookMetadata(
                    title=full_title,  # Titre complet avec série
                    short_title=title,    # Titre court (sans série)
                    author=author,
                    series=series,
                    series_number=series_number,
                    genre="Audiobook",
                    language="fr"
                )
                
                logger.info(f"🔍 Parsing série: {author} - {series} - {volume_text} - {title}")
                return metadata
        
        # Pattern 2: Auteur - Titre simple (si pas de série détectée)
        match = re.match(r'^([^–-]+)\s*[–-]\s*(.+)$', filename_clean, re.IGNORECASE)
        if match:
            author = self.normalize_filename(match.group(1).strip())
            title = self.normalize_filename(match.group(2).strip())
            
            metadata = AudiobookMetadata(
                title=title,
                author=author,
                genre="Audiobook",
                language="fr"
            )
            
            logger.info(f"🔍 Parsing simple: {author} - {title}")
            return metadata
        
        # Pattern 2: Auteur - Série Tome X - Titre
        match = re.match(r'^([^–-]+)\s*[–-]\s*([^–-]+)\s+(?:tome|volume|part)\s+(\d+)\s*[–-]\s*(.+)$', filename_clean, re.IGNORECASE)
        if match:
            author = self.normalize_filename(match.group(1).strip())
            series = self.normalize_filename(match.group(2).strip())
            series_number = match.group(3)
            title = self.normalize_filename(match.group(4).strip())
            
            metadata = AudiobookMetadata(
                title=title,
                author=author,
                series=series,
                series_number=series_number,
                genre="Audiobook",
                language="fr"
            )
            
            logger.info(f"🔍 Parsing série explicite: {author} - {series} Tome {series_number} - {title}")
            return metadata
        
        # Pattern 3: Format avec narrateur: Auteur - Titre (lu par Narrateur)
        match = re.match(r'^([^–-]+)\s*[–-]\s*([^-(]+)\s*\(\s*lu\s+par\s+([^)]+)\s*\)$', filename_clean, re.IGNORECASE)
        if match:
            author = self.normalize_filename(match.group(1).strip())
            title = self.normalize_filename(match.group(2).strip())
            narrator = self.normalize_filename(match.group(3).strip())
            
            metadata = AudiobookMetadata(
                title=title,
                author=author,
                narrator=narrator,
                genre="Audiobook",
                language="fr"
            )
            
            logger.info(f"🔍 Parsing avec narrateur: {author} - {title} (lu par {narrator})")
            return metadata
        
        # Fallback: utilise le nom de fichier comme titre
        logger.warning(f"⚠️ Parsing échoué, utilisation du nom de fichier: {filename_clean}")
        return AudiobookMetadata(
            title=self.normalize_filename(filename_clean),
            author="Inconnu",
            genre="Audiobook",
            language="fr"
        )
    
    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Extrait une archive (zip/rar)"""
        try:
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix.lower() == '.rar':
                with rarfile.RarFile(archive_path, 'r') as rar_ref:
                    rar_ref.extractall(extract_to)
            else:
                return False
            return True
        except Exception as e:
            logger.error(f"Erreur extraction {archive_path}: {e}")
            return False
    
    def find_audio_files(self, directory: Path) -> List[Path]:
        """Trouve tous les fichiers audio dans un répertoire"""
        audio_extensions = {'.mp3', '.m4a', '.wav', '.flac', '.aac'}
        audio_files = []
        
        # Recherche dans le dossier courant et les sous-dossiers
        for ext in audio_extensions:
            # Fichiers directement dans le dossier
            audio_files.extend(directory.glob(f'*{ext}'))
            # Fichiers dans les sous-dossiers
            audio_files.extend(directory.rglob(f'*{ext}'))
        
        # Supprime les doublons et trie
        audio_files = list(set(audio_files))
        audio_files.sort(key=lambda x: (x.parent.name, x.name))
        
        return audio_files
    
    def convert_to_m4b(self, audio_files: List[Path], output_path: Path, metadata: AudiobookMetadata) -> bool:
        """Convertit des fichiers audio en M4B avec métadonnées et accélération GPU HAUTE QUALITÉ"""
        try:
            logger.info(f"🎵 DÉBUT CONVERSION HAUTE QUALITÉ: {len(audio_files)} fichiers vers {output_path.name}")
            
            # Crée la liste des fichiers pour ffmpeg
            file_list = self.temp_dir / "filelist.txt"
            with open(file_list, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file.absolute()}'\n")
            
            # Récupération de la configuration
            config = getattr(self, 'config', ProcessingConfig())
            
            # Construction métadonnées complètes
            metadata_dict = metadata.get_metadata_dict()
            metadata_args = []
            for key, value in metadata_dict.items():
                metadata_args.extend(['-metadata', f'{key}={value}'])
            
            logger.info(f"📝 Métadonnées: {len(metadata_dict)} champs")
            logger.info(f"   📚 Titre: {metadata.title}")
            logger.info(f"   ✍️  Auteur: {metadata.author}")
            if metadata.narrator:
                logger.info(f"   🎤 Narrateur: {metadata.narrator}")
            if metadata.series:
                logger.info(f"   📖 Série: {metadata.series} Tome {metadata.series_number}")
            if metadata.year:
                logger.info(f"   📅 Année: {metadata.year}")
            if metadata.publisher:
                logger.info(f"   🏢 Éditeur: {metadata.publisher}")
            
            # Vérification du codec audio avancé
            use_fdk = self.check_fdk_aac()
            
            # Construction des filtres audio
            audio_filters = []
            if config.enable_loudnorm:
                # Normalisation EBU R128 pour audiobooks
                loudnorm_filter = f"loudnorm=I={config.loudnorm_target}:TP=-1.5:LRA={config.loudnorm_range}"
                audio_filters.append(loudnorm_filter)
                logger.info(f"🔊 Normalisation audio activée: {config.loudnorm_target} LUFS")
            
            if config.enable_compressor:
                # Compression dynamique pour voix
                audio_filters.append(config.compressor_settings)
                logger.info("🎛️ Compression dynamique activée")
            
            # Désactive les filtres si demandé
            if not config.enable_loudnorm:
                logger.info("🔊 Normalisation audio désactivée")
            if not config.enable_compressor:
                logger.info("🎛️ Compression dynamique désactivée")
            
            filter_string = ",".join(audio_filters) if audio_filters else None
            
            # Détection et configuration GPU
            use_gpu = config.enable_gpu_acceleration and self.detect_gpu_acceleration()
            
            # Pour les audiobooks, le GPU aide principalement pour les filtres audio
            # L'encodage audio reste CPU (AAC/FDK-AAC) pour la meilleure qualité
            if use_gpu:
                logger.info("🚀 UTILISATION GPU NVIDIA RTX 4070 - FILTRES AUDIO ACCÉLÉRÉS")
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(file_list),
                    # Filtres audio avec accélération GPU si disponible
                    *(['-af', filter_string] if filter_string else []),
                    # Audio HAUTE QUALITÉ CPU (GPU ne peut pas encoder l'audio)
                    '-c:a', 'libfdk_aac' if self.check_fdk_aac() else 'aac',
                    '-b:a', config.audio_bitrate,
                    '-ac', str(config.audio_channels),
                    '-ar', str(config.sample_rate),
                    '-aac_coder', config.aac_coder,
                    '-cutoff', str(config.cutoff_freq),
                    # VBR si FDK disponible
                    *(['-vbr', '4'] if self.check_fdk_aac() else []),
                    # Paramètres d'optimisation
                    '-movflags', '+faststart',
                    # Métadonnées
                    *metadata_args,
                    '-progress', 'pipe:1',
                    '-f', 'mp4',
                    str(output_path)
                ]
                codec_info = f"FDK-AAC VBR4 + GPU RTX 4070" if self.check_fdk_aac() else f"AAC + GPU RTX 4070"
            else:
                logger.info("⚙️ UTILISATION CPU HAUTE QUALITÉ AUDIO")
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(file_list),
                    # Filtres audio si présents
                    *(['-af', filter_string] if filter_string else []),
                    # Audio haute qualité CPU
                    '-c:a', 'libfdk_aac' if self.check_fdk_aac() else 'aac',
                    '-b:a', config.audio_bitrate,
                    '-ac', str(config.audio_channels),
                    '-ar', str(config.sample_rate),
                    '-aac_coder', config.aac_coder,
                    '-cutoff', str(config.cutoff_freq),
                    # VBR si FDK disponible
                    *(['-vbr', '4'] if self.check_fdk_aac() else []),
                    # Métadonnées
                    *metadata_args,
                    '-progress', 'pipe:1',
                    '-f', 'mp4',
                    str(output_path)
                ]
            # Calcule la taille totale des fichiers source
            total_input_size = 0
            for audio_file in audio_files:
                try:
                    total_input_size += audio_file.stat().st_size
                except OSError:
                    continue
            
            total_input_mb = total_input_size / (1024*1024)
            logger.info(f'📊 Taille totale source: {total_input_mb:.1f}MB ({len(audio_files)} fichiers)')
            
            # Lance FFmpeg avec surveillance active
            logger.info("🚀 LANCEMENT FFmpeg - Surveillance CPU/GPU active...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            # Suivi de progression simple et efficace
            start_time = time.time()
            last_size = 0
            last_progress_time = 0
            
            while True:
                # Vérifie si le processus est terminé
                if process.poll() is not None:
                    break
                
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Condition d'arrêt: si progression > 90% ET temps > 30 secondes
                if elapsed > 30:
                    if output_path.exists():
                        current_size = output_path.stat().st_size / (1024*1024)
                        estimated_final_size = total_input_mb * (0.3 if '64k' in config.audio_bitrate else 0.6)
                        if current_size > estimated_final_size * 0.9:
                            logger.info("🎯 SEUIL D'ARRÊT ATTEINT - Finalisation...")
                            break
                
                # Affiche progression chaque 3 secondes (plus fréquent)
                if current_time - last_progress_time >= 3:
                    try:
                        # Vérifie la taille du fichier de sortie
                        if output_path.exists():
                            current_size = output_path.stat().st_size / (1024*1024)  # MB
                            
                            # Calcule la progression basée sur la taille estimée
                            if current_size > 0.1:  # Évite les faux positifs
                                # Estimation de la taille finale basée sur le bitrate
                                estimated_final_size = total_input_mb * (0.3 if '64k' in config.audio_bitrate else 0.6)
                                progress = min(95, (current_size / max(1, estimated_final_size)) * 100)
                                
                                # Barre de progression
                                bar_length = 25
                                filled = int(bar_length * progress / 100)
                                bar = '█' * filled + '░' * (bar_length - filled)
                                
                                elapsed = int(current_time - start_time)
                                minutes = elapsed // 60
                                seconds = elapsed % 60
                                
                                # Calcule la vitesse de création
                                speed_mbps = (current_size - last_size) / 3 if current_size > last_size else 0
                                
                                # Détection d'activité CPU/GPU
                                if speed_mbps > 5:
                                    activity = "🔥 ACTIF"
                                elif speed_mbps > 2:
                                    activity = "⚡ NORMAL"
                                elif speed_mbps > 0.5:
                                    activity = "🐢 LENT"
                                else:
                                    activity = "⏸️ PAUSE"
                                
                                logger.info(f'🎵 [{bar}] {progress:3.0f}% | '
                                          f'Source: {total_input_mb:.1f}MB → '
                                          f'Sortie: {current_size:6.1f}MB | '
                                          f'+{speed_mbps:.1f}MB/s | '
                                          f'{minutes:02d}:{seconds:02d} | {activity}')
                                
                                last_size = current_size
                                last_progress_time = current_time
                    
                    except (OSError, PermissionError):
                        continue
                
                # Petite pause pour ne pas surcharger le CPU
                time.sleep(0.5)
            
            # Attend la fin du processus
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f'❌ Erreur FFmpeg: {stderr}')
                raise Exception(f'Échec de la conversion FFmpeg: {stderr}')
            
            # Calcul des statistiques finales
            total_time = time.time() - start_time
            input_size = sum(f.stat().st_size for f in audio_files) / (1024*1024)  # MB
            output_size = output_path.stat().st_size / (1024*1024) if output_path.exists() else 0  # MB
            
            logger.info(f"✅ Conversion FFmpeg terminée en {total_time//60:.0f}m{total_time%60:.0f}s")
            logger.info(f"📊 Qualité: {codec_info} | {config.audio_bitrate} | {config.audio_channels} canaux | {config.sample_rate}Hz")
            logger.info(f"📊 Compression: {input_size:.1f}MB → {output_size:.1f}MB ({((1-output_size/input_size)*100):.1f}%)")
            
            # Analyse des performances
            avg_speed = output_size / (total_time / 60) if total_time > 0 else 0
            if avg_speed > 50:
                logger.info(f"� PERFORMANCE: EXCELLENTE ({avg_speed:.1f} MB/min)")
            elif avg_speed > 20:
                logger.info(f"⚡ PERFORMANCE: BONNE ({avg_speed:.1f} MB/min)")
            elif avg_speed > 10:
                logger.info(f"🐢 PERFORMANCE: LENTE ({avg_speed:.1f} MB/min)")
            else:
                logger.info(f"⏸️ PERFORMANCE: TRÈS LENTE ({avg_speed:.1f} MB/min)")
            
            # Ajout de la pochette si disponible
            if metadata.cover_path and Path(metadata.cover_path).exists():
                logger.info("🖼️ Ajout de la pochette...")
                if self.add_cover_to_m4b(output_path, metadata.cover_path):
                    logger.info("✅ Pochette intégrée avec succès")
                else:
                    logger.warning("⚠️ Échec ajout pochette")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Erreur conversion M4B: {e}")
            return False
    
    def check_fdk_aac(self) -> bool:
        """Vérifie si le codec FDK-AAC est disponible"""
        try:
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                 capture_output=True, text=True, timeout=5)
            return 'libfdk_aac' in result.stdout
        except:
            return False
    
    def detect_gpu_acceleration(self) -> bool:
        """Détecte si l'accélération GPU NVIDIA RTX 4070 est disponible"""
        try:
            # Test si NVENC est disponible
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                 capture_output=True, text=True, timeout=5)
            if 'h264_nvenc' in result.stdout:
                # Vérifie les GPUs NVIDIA disponibles
                nvidia_result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                          capture_output=True, text=True, timeout=5)
                if nvidia_result.returncode == 0 and nvidia_result.stdout.strip():
                    gpu_list = [gpu.strip() for gpu in nvidia_result.stdout.strip().split('\n') if gpu.strip()]
                    logger.info(f"🎮 GPUs détectés: {', '.join(gpu_list)}")
                    
                    for gpu_name in gpu_list:
                        if '4070' in gpu_name:
                            logger.info(f"✅ GPU NVIDIA RTX 4070 trouvé: {gpu_name}")
                            return True
                        elif '3050' in gpu_name:
                            logger.info(f"✅ GPU NVIDIA RTX 3050 trouvé: {gpu_name}")
                            logger.info(f"⚠️ RTX 3050 non trouvé, utilisation de: {gpu_name}")
                            return True
                    
                    logger.warning("❌ Aucun GPU NVIDIA compatible trouvé")
                    return False
                else:
                    logger.warning("⚠️ nvidia-smi non disponible")
                    return False
            else:
                logger.warning("⚠️ NVENC non disponible dans FFmpeg")
                return False
        except Exception as e:
            logger.error(f"Erreur détection GPU: {e}")
            return False
    
    def add_cover_to_m4b(self, m4b_path: Path, cover_path: str) -> bool:
        """Ajoute une pochette à un fichier M4B"""
        try:
            # Redimensionne la pochette
            with Image.open(cover_path) as img:
                img = img.convert('RGB')
                img = img.resize((600, 600), Image.Resampling.LANCZOS)
                
                cover_temp = self.temp_dir / "cover_temp.jpg"
                img.save(cover_temp, 'JPEG', quality=85)
            
            # Ajout avec mutagen
            audio = MP4(m4b_path)
            with open(cover_temp, 'rb') as f:
                audio['covr'] = [MP4Cover(f.read(), MP4Cover.FORMAT_JPEG)]
            audio.save()
            
            return True
        except Exception as e:
            logger.error(f"Erreur ajout pochette: {e}")
            return False
    
    def scrap_book_info(self, metadata: AudiobookMetadata) -> AudiobookMetadata:
        """Enrichit les métadonnées avec le scraping web"""
        try:
            logger.info("🌐 Scraping web pour enrichir les métadonnées...")
            
            from scraper import BookScraper
            scraper = BookScraper()
            
            # Recherche sur Babelio
            book_info = scraper.search_book(metadata.author, metadata.title)
            
            if book_info:
                logger.info("✅ Informations trouvées sur Babelio")
                
                # Mise à jour des métadonnées
                if book_info.publisher:
                    metadata.publisher = book_info.publisher
                    logger.info(f"   📚 Éditeur: {book_info.publisher}")
                
                if book_info.publication_date:
                    # Extraction de l'année
                    year_match = re.search(r'(\d{4})', book_info.publication_date)
                    if year_match:
                        metadata.year = year_match.group(1)
                        logger.info(f"   📅 Année: {metadata.year}")
                
                if book_info.description:
                    metadata.description = book_info.description
                    logger.info(f"   📝 Description: {len(book_info.description)} caractères")
                
                if book_info.cover_url:
                    # Téléchargement de la pochette
                    cover_path = self.temp_dir / f"cover_{int(time.time())}.jpg"
                    if scraper.babelio.download_cover(book_info.cover_url, str(cover_path)):
                        metadata.cover_path = str(cover_path)
                        logger.info(f"   🖼️ Pochette téléchargée: {cover_path}")
                
                if book_info.genres:
                    metadata.genre = ", ".join(book_info.genres[:3])  # Top 3 genres
                    logger.info(f"   🏷️ Genres: {metadata.genre}")
                
                if book_info.series:
                    metadata.series = book_info.series
                    logger.info(f"   📖 Série: {book_info.series}")
                
                if book_info.rating:
                    logger.info(f"   ⭐ Note: {book_info.rating}/5")
                
                return metadata
            else:
                logger.warning("⚠️ Aucune information trouvée sur Babelio")
                return metadata
                
        except Exception as e:
            logger.error(f"💥 Erreur scraping: {e}")
            return metadata
    
    def generate_synopsis(self, metadata: AudiobookMetadata) -> str:
        """Génère un synopsis avec Ollama"""
        try:
            prompt = f"""Génère un synopsis court et sans spoiler pour le livre "{metadata.title}" de {metadata.author}.
            Le synopsis doit faire environ 150-200 mots, être en français, et donner envie de lire le livre
            sans révéler les rebondissements importants de l'intrigue."""
            
            cmd = ['ollama', 'run', 'llama2', prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except Exception as e:
            logger.error(f"Erreur génération synopsis: {e}")
        
        return f"Synopsis de {metadata.title} par {metadata.author}"
    
    def download_cover(self, metadata: AudiobookMetadata) -> Optional[str]:
        """Télécharge une pochette de bonne qualité ou utilise celle existante"""
        # Vérifie d'abord si une pochette a déjà été téléchargée
        if hasattr(metadata, 'cover_path') and metadata.cover_path:
            cover_path = Path(metadata.cover_path)
            if cover_path.exists():
                logger.info(f"   ✅ Pochette déjà disponible: {cover_path}")
                return str(cover_path)
        
        # Si aucune pochette n'existe, retourne None
        logger.info("   ⚠️ Aucune pochette disponible")
        return None
    
    def parse_audiobook_metadata(self, filename: str) -> AudiobookMetadata:
        """Extrait les métadonnées d'un nom de fichier audiobook"""
        return self.parse_filename(filename)
    
    def process_audiobook(self, file_path: Path) -> bool:
        """Traite un fichier audiobook complet"""
        try:
            logger.info(f"🚀 DÉBUT DU TRAITEMENT: {file_path.name}")
            logger.info(f"📁 Chemin complet: {file_path}")
            logger.info(f"📊 Type: {'DOSSIER' if file_path.is_dir() else 'FICHIER'}")
            
            # 1. Extraction métadonnées de base
            logger.info("🔍 ÉTAPE 1: Analyse des métadonnées depuis le nom...")
            metadata = self.parse_filename(file_path.name)
            logger.info(f"   ✅ Auteur détecté: '{metadata.author}'")
            logger.info(f"   ✅ Titre détecté: '{metadata.title}'")
            if metadata.series:
                logger.info(f"   ✅ Série: '{metadata.series}' Tome {metadata.series_number}")
            
            # 2. Création répertoire de travail
            logger.info("📂 ÉTAPE 2: Préparation de l'espace de travail...")
            work_dir = self.temp_dir / file_path.stem
            work_dir.mkdir(exist_ok=True)
            logger.info(f"   📁 Dossier temporaire: {work_dir}")
            
            # 3. Gestion du type de fichier
            logger.info("🔎 ÉTAPE 3: Recherche des fichiers audio...")
            audio_files = []
            
            if file_path.is_file():
                logger.info("   📄 Type: Fichier unique détecté")
                if file_path.suffix.lower() in ['.zip', '.rar']:
                    logger.info(f"   📦 Archive {file_path.suffix} détectée - Extraction en cours...")
                    if not self.extract_archive(file_path, work_dir):
                        logger.error(f"❌ Échec extraction de {file_path}")
                        return False
                    logger.info("   ✅ Archive extraite avec succès")
                    audio_files = self.find_audio_files(work_dir)
                elif file_path.suffix.lower() in ['.mp3', '.m4a', '.wav', '.flac', '.aac']:
                    logger.info(f"   🎵 Fichier audio direct: {file_path.name}")
                    audio_files = [file_path]
                else:
                    logger.warning(f"⚠️ Type de fichier non supporté: {file_path.suffix}")
                    return False
                    
            elif file_path.is_dir():
                logger.info("   📁 Type: Dossier contenant des fichiers audio")
                logger.info(f"   🔍 Recherche récursive dans: {file_path}")
                audio_files = self.find_audio_files(file_path)
            
            # 4. Vérification des fichiers audio
            logger.info(f"📊 ÉTAPE 4: Analyse des fichiers audio trouvés...")
            if not audio_files:
                logger.error(f"❌ Aucun fichier audio trouvé dans {file_path}")
                return False
            
            logger.info(f"   ✅ {len(audio_files)} fichiers audio détectés")
            total_size = sum(f.stat().st_size for f in audio_files)
            logger.info(f"   📏 Taille totale: {total_size / 1_000_000:.1f} MB")
            
            # Affiche TOUS les fichiers avec progression
            logger.info(f"   📋 Liste complète des {len(audio_files)} fichiers audio:")
            for i, audio_file in enumerate(audio_files):
                size_mb = audio_file.stat().st_size / 1_000_000
                logger.info(f"      {i+1:2d}. {audio_file.name} ({size_mb:.1f} MB)")
            
            # 5. Enrichissement métadonnées
            logger.info("🌐 ÉTAPE 5: Enrichissement des métadonnées...")
            if hasattr(self, 'config') and self.config.enable_scraping:
                logger.info("   🔍 Scraping web activé - Recherche d'informations...")
                metadata = self.scrap_book_info(metadata)
            else:
                logger.info("   ⏭️ Scraping désactivé")
            
            # 6. Téléchargement pochette
            logger.info("🖼️ ÉTAPE 6: Gestion de la pochette...")
            if hasattr(self, 'config') and self.config.enable_scraping:
                logger.info("   🔍 Recherche d'une pochette...")
                cover_path = self.download_cover(metadata)
                if cover_path:
                    metadata.cover_path = cover_path
                    logger.info(f"   ✅ Pochette trouvée: {cover_path}")
                else:
                    logger.info("   ⚠️ Aucune pochette trouvée")
            else:
                logger.info("   ⏭️ Recherche de pochette désactivée")
            
            # 7. Conversion M4B
            logger.info("🔄 ÉTAPE 7: Conversion vers M4B...")
            output_filename = f"{metadata.get_filename_format()}.m4b"
            output_path = self.output_dir / output_filename
            logger.info(f"   📁 Fichier de sortie: {output_path}")
            logger.info(f"   ⚙️ Bitrate: {getattr(self.config, 'audio_bitrate', '128k') if hasattr(self, 'config') else '128k'}")
            
            success = self.convert_to_m4b(audio_files, output_path, metadata)
            
            if success:
                final_size = output_path.stat().st_size if output_path.exists() else 0
                logger.info(f"✅ SUCCÈS: {output_filename}")
                logger.info(f"   📏 Taille finale: {final_size / 1_000_000:.1f} MB")
                logger.info(f"   📍 Emplacement: {output_path}")
                return True
            else:
                logger.error(f"❌ ÉCHEC conversion: {file_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"💥 ERREUR critique lors du traitement de {file_path}: {e}")
            return False
        finally:
            # Nettoyage
            logger.info("🧹 NETTOYAGE: Suppression des fichiers temporaires...")
            if 'work_dir' in locals() and work_dir.exists():
                shutil.rmtree(work_dir)
                logger.info(f"   🗑️ Dossier temporaire supprimé: {work_dir}")
    
    def process_all(self) -> Dict[str, int]:
        """Traite tous les audiobooks du dossier source"""
        logger.info("🚀 DÉBUT DU TRAITEMENT GLOBAL")
        logger.info(f"📁 Dossier source: {self.source_dir}")
        logger.info(f"📁 Dossier de sortie: {self.output_dir}")
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        # Crée dossier de sortie
        self.output_dir.mkdir(exist_ok=True)
        logger.info("✅ Dossier de sortie prêt")
        
        # Analyse préliminaire
        logger.info("🔍 ANALYSE PRÉLIMINAIRE DU DOSSIER...")
        all_items = list(self.source_dir.iterdir())
        logger.info(f"   📊 {len(all_items)} éléments trouvés")
        
        files_to_process = []
        folders_to_process = []
        
        for item in all_items:
            if item.is_file():
                if item.suffix.lower() in ['.zip', '.rar', '.mp3', '.m4a', '.m4b']:
                    files_to_process.append(item)
                else:
                    results["skipped"] += 1
            elif item.is_dir():
                # Vérifie si le dossier contient des fichiers audio
                audio_count = len(self.find_audio_files(item))
                if audio_count > 0:
                    folders_to_process.append(item)
                    logger.info(f"   📁 Dossier avec {audio_count} fichiers audio: {item.name}")
                else:
                    results["skipped"] += 1
            else:
                results["skipped"] += 1
        
        total_to_process = len(files_to_process) + len(folders_to_process)
        logger.info(f"📋 RÉCAPITULATIF:")
        logger.info(f"   📄 Fichiers à traiter: {len(files_to_process)}")
        logger.info(f"   📁 Dossiers à traiter: {len(folders_to_process)}")
        logger.info(f"   ⏭️ Éléments ignorés: {results['skipped']}")
        logger.info(f"   🎯 Total à traiter: {total_to_process}")
        
        # Traitement des dossiers d'abord
        if folders_to_process:
            logger.info(f"\n📁 TRAITEMENT DES {len(folders_to_process)} DOSSIERS...")
            for i, folder_path in enumerate(folders_to_process, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"📂 DOSSIER {i}/{len(folders_to_process)}: {folder_path.name}")
                logger.info(f"📊 Progression globale: {i-1}/{len(folders_to_process) + len(files_to_process)} éléments traités")
                logger.info(f"{'='*60}")
                
                start_time = time.time()
                if self.process_audiobook(folder_path):
                    results["success"] += 1
                    elapsed = time.time() - start_time
                    logger.info(f"✅ Dossier traité en {elapsed//60:.0f}m{elapsed%60:.0f}s")
                else:
                    results["failed"] += 1
                    elapsed = time.time() - start_time
                    logger.error(f"❌ Échec du dossier après {elapsed//60:.0f}m{elapsed%60:.0f}s")
        
        # Traitement des fichiers
        if files_to_process:
            logger.info(f"\n📄 TRAITEMENT DES {len(files_to_process)} FICHIERS...")
            for i, file_path in enumerate(files_to_process, 1):
                global_progress = len(folders_to_process) + i - 1
                logger.info(f"\n{'='*60}")
                logger.info(f"📃 FICHIER {i}/{len(files_to_process)}: {file_path.name}")
                logger.info(f"📊 Progression globale: {global_progress}/{len(folders_to_process) + len(files_to_process)} éléments traités")
                logger.info(f"{'='*60}")
                
                start_time = time.time()
                if self.process_audiobook(file_path):
                    results["success"] += 1
                    elapsed = time.time() - start_time
                    logger.info(f"✅ Fichier traité en {elapsed//60:.0f}m{elapsed%60:.0f}s")
                else:
                    results["failed"] += 1
                    elapsed = time.time() - start_time
                    logger.error(f"❌ Échec du fichier après {elapsed//60:.0f}m{elapsed%60:.0f}s")
        
        # Résultats finaux
        logger.info("\n" + "="*60)
        logger.info("🏁 TRAITEMENT TERMINÉ")
        logger.info("📊 RÉSULTATS FINAUX:")
        logger.info(f"   ✅ Succès: {results['success']}")
        logger.info(f"   ❌ Échecs: {results['failed']}")
        logger.info(f"   ⏭️ Ignorés: {results['skipped']}")
        logger.info(f"   📁 Fichiers créés dans: {self.output_dir}")
        
        return results

if __name__ == "__main__":
    # Configuration
    SOURCE_DIR = "/home/fabrice/Documents/Audiobooks"
    OUTPUT_DIR = "/home/fabrice/Documents/Audiobooks_Processed"  # Dossier séparé pour les fichiers traités
    TEMP_DIR = "/tmp/audiobooks"
    
    # Crée le dossier de sortie s'il n'existe pas
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    processor = AudiobookProcessor(SOURCE_DIR, OUTPUT_DIR, TEMP_DIR)
    results = processor.process_all()
    
    print("\n📊 Résultats du traitement:")
    print(f"✅ Succès: {results['success']}")
    print(f"❌ Échecs: {results['failed']}")
    print(f"⏭️ Ignorés: {results['skipped']}")
    print(f"📁 Fichiers traités disponibles dans: {OUTPUT_DIR}")
