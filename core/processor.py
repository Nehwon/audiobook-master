#!/usr/bin/env python3
"""
Système complet de traitement d'audiobooks - Version Optimisée OPUS
- Renommage automatique
- Conversion OPUS (meilleur rapport taille/qualité)
- Métadonnées rapides
- Pochettes
- Surveillance CPU/GPU temps réel
"""

import os
import re
import json
import shutil
import subprocess
import requests
import time
import psutil
import threading
import gc
import weakref
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
from .config import ProcessingConfig

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AudiobookMetadata:
    """Métadonnées complètes d'un audiobook"""
    # Identification principale
    title: str
    author: str
    short_title: Optional[str] = None
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
    
    # Chapitres
    chapters: Optional[List[Dict]] = None
    
    def get_filename_format(self) -> str:
        """Génère le nom de fichier selon les conventions"""
        if self.series and self.series_number:
            return f"{self.author} - {self.series} - Tome {self.series_number} - {self.title}"
        else:
            return f"{self.author} - {self.title}"
    
    def get_metadata_dict(self) -> Dict[str, str]:
        """Retourne les métadonnées au format FFmpeg"""
        metadata = {
            'title': self.title,
            'artist': self.narrator or self.author,
            'albumartist': self.author,
            'album': self.series or self.title,
            'genre': self.genre or "Audiobook",
            'date': self.year or "",
            'encodedby': "FFmpeg OPUS optimized",
            'comment': self.description or "",
            'publisher': self.publisher or "",
            'language': self.language,
            'description': self.description or "",
        }
        
        if self.series:
            metadata['series'] = self.series
            if self.series_number:
                metadata['seriespart'] = self.series_number
                metadata['track'] = f"{self.series_number}"
        
        return {k: v for k, v in metadata.items() if v}

class AudiobookProcessor:
    def __init__(self, source_dir: str, output_dir: str, temp_dir: str = "/tmp/audiobooks"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def normalize_filename(self, filename: str) -> str:
        """Normalise un nom de fichier"""
        filename = unicodedata.normalize('NFKD', filename)
        filename = ''.join(c for c in filename if not unicodedata.combining(c))
        filename = re.sub(r'[^\w\s\-_.]', '', filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        return filename
    
    def parse_filename(self, filename: str) -> AudiobookMetadata:
        """Extrait les métadonnées de base du nom de fichier"""
        filename_clean = re.sub(r'\.(zip|rar|mp3|m4a|m4b)$', '', filename)
        filename_clean = filename_clean.replace('_', ' ')
        filename_clean = re.sub(r'\[.*?\]', '', filename_clean)
        filename_clean = re.sub(r'\([^)]*\)', '', filename_clean)
        filename_clean = re.sub(r'\s+', ' ', filename_clean).strip()
        
        # Pattern Auteur - Titre
        match = re.match(r'^([^–-]+)\s*[–-]\s*(.+)$', filename_clean, re.IGNORECASE)
        if match:
            author = self.normalize_filename(match.group(1).strip())
            title = self.normalize_filename(match.group(2).strip())
            
            return AudiobookMetadata(
                title=title,
                author=author,
                genre="Audiobook",
                language="fr"
            )
        
        # Fallback
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
        """Trouve tous les fichiers audio dans un répertoire et sous-dossiers"""
        audio_extensions = {'.mp3', '.m4a', '.wav', '.flac', '.aac'}
        audio_files = []
        
        # rglob() suffit - il trouve les fichiers dans le dossier ET tous les sous-dossiers
        for ext in audio_extensions:
            audio_files.extend(directory.rglob(f'*{ext}'))
        
        # Supprime les doublons (sécurité)
        audio_files = list(set(audio_files))
        audio_files.sort(key=lambda x: (x.parent.name, x.name))
        
        return audio_files
    
    def check_aac_support(self) -> bool:
        """Vérifie si le codec AAC est disponible"""
        try:
            result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                                 capture_output=True, text=True, timeout=5)
            return 'aac' in result.stdout
        except:
            return False
    
    def detect_cuda_support(self) -> bool:
        """Détecte si CUDA est disponible"""
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '4070' in line:
                        logger.info(f"✅ CUDA RTX 4070 détecté: {line}")
                        return True
            return False
        except:
            return False
    
    def concat_fast_m4b(self, audio_files: List[Path], output_path: Path, metadata: AudiobookMetadata) -> bool:
        """Concaténation 1:1 rapide sans réencodage - Phase 1"""
        try:
            logger.info(f"🚀 CONCATÉNATION 1:1 RAPIDE: {len(audio_files)} fichiers")
            
            # Surveillance système
            stop_monitoring = threading.Event()
            system_stats = {'cpu_percent': 0, 'ram_mb': 0}
            
            def monitor_system():
                while not stop_monitoring.is_set():
                    try:
                        system_stats['cpu_percent'] = psutil.cpu_percent(interval=0.5)
                        memory = psutil.virtual_memory()
                        system_stats['ram_mb'] = memory.used / (1024*1024)
                        time.sleep(2)
                    except:
                        break
            
            monitor_thread = threading.Thread(target=monitor_system, daemon=True)
            monitor_thread.start()
            
            # Crée la liste des fichiers pour ffmpeg
            file_list = self.temp_dir / "filelist.txt"
            with open(file_list, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file.absolute()}'\n")
            
            # Configuration
            config = getattr(self, 'config', ProcessingConfig())
            max_threads = os.cpu_count() or 24
            
            # Métadonnées
            metadata_dict = metadata.get_metadata_dict()
            metadata_args = []
            for key, value in metadata_dict.items():
                metadata_args.extend(['-metadata', f'{key}={value}'])
            
            # Commande FFmpeg CONCATÉNATION RAPIDE (sans réencodage)
            logger.info("⚡ CONCATÉNATION SANS RÉENCODAGE - VITESSE MAXIMALE")
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list),
                '-c', 'copy',  # COPIE DIRECTE - PAS DE RÉENCODAGE
                '-map_metadata', '0',  # Conserve métadonnées originales
                # Métadonnées enrichies
                *metadata_args,
                '-progress', 'pipe:1',
                '-f', 'mp4',
                str(output_path)
            ]
            
            codec_info = "CONCAT 1:1 (COPY) - VITESSE MAXIMALE"
            
            # Taille totale
            total_input_size = sum(f.stat().st_size for f in audio_files)
            total_input_mb = total_input_size / (1024*1024)
            logger.info(f'📊 Taille source: {total_input_mb:.1f}MB')
            logger.info(f'📊 Taille attendue: ~{total_input_mb:.1f}MB (identique)')
            
            # Lance FFmpeg
            logger.info("🚀 LANCEMENT CONCATÉNATION...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            # Suivi de progression rapide
            start_time = time.time()
            last_stats_time = 0
            timeout = 1800  # 30 minutes max pour concaténation
            
            while True:
                if process.poll() is not None:
                    break
                
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Timeout de sécurité
                if elapsed > timeout:
                    logger.error(f"❌ TIMEOUT concaténation après {timeout/60:.0f} minutes")
                    process.terminate()
                    break
                
                # Stats système toutes les 5 secondes (plus rapide)
                if (current_time - last_stats_time) > 5:
                    cpu = system_stats['cpu_percent']
                    ram = system_stats['ram_mb']
                    
                    if output_path.exists():
                        data = output_path.stat().st_size / (1024*1024)
                        progress_percent = min(100, (data / total_input_mb) * 100)
                        
                        # Vitesse de concaténation (très rapide)
                        if elapsed > 10 and data > 1:
                            speed_mbps = data / (elapsed / 60)
                            speed_str = f"{speed_mbps:.1f}MB/min"
                            eta_minutes = (total_input_mb - data) / speed_mbps if speed_mbps > 0 else 0
                            eta_str = f"{int(eta_minutes)}mn" if eta_minutes > 0 else "<1mn"
                        else:
                            data = 0
                            progress_percent = 0
                            speed_str = "--"
                            eta_str = "--"
                        
                        # Barre de progression
                        bar_length = 30
                        filled = int(bar_length * progress_percent / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        
                        logger.info(f"⚡ [{bar}] {progress_percent:3.0f}% | {data:6.1f}MB/{total_input_mb:.1f}MB | {speed_str} | ETA {eta_str}")
                        last_stats_time = current_time
                
                time.sleep(0.2)  # Très réactif
            
            # Arrêt surveillance et nettoyage
            stop_monitoring.set()
            monitor_thread.join(timeout=2)
            
            # Force l'arrêt du processus FFmpeg s'il est encore actif
            if process.poll() is None:
                logger.warning("🔄 Force arrêt processus FFmpeg...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.error("💥 Force KILL processus FFmpeg...")
                    process.kill()
                    process.wait()
            
            # Nettoyage mémoire
            gc.collect()
            logger.info("🧹 Nettoyage mémoire effectué")
            
            # Attend la fin
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f'❌ Erreur FFmpeg: {stderr}')
                return False
            
            # Statistiques finales
            total_time = time.time() - start_time
            input_size = total_input_size / (1024*1024)
            output_size = output_path.stat().st_size / (1024*1024) if output_path.exists() else 0
            
            logger.info(f"✅ Concaténation terminée en {total_time//60:.0f}m{total_time%60:.0f}s")
            logger.info(f"📊 Mode: {codec_info}")
            logger.info(f"📊 Taille finale: {input_size:.1f}MB → {output_size:.1f}MB ({((output_size/input_size)*100):.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Erreur concaténation: {e}")
            return False
        """Convertit des fichiers audio en M4B avec optimisations AAC HAUTE QUALITÉ"""
        try:
            logger.info(f"🎵 CONVERSION M4B HAUTE QUALITÉ: {len(audio_files)} fichiers")
            
            # Surveillance système
            stop_monitoring = threading.Event()
            system_stats = {'cpu_percent': 0, 'ram_mb': 0}
            
            def monitor_system():
                while not stop_monitoring.is_set():
                    try:
                        system_stats['cpu_percent'] = psutil.cpu_percent(interval=0.5)
                        memory = psutil.virtual_memory()
                        system_stats['ram_mb'] = memory.used / (1024*1024)
                        time.sleep(2)
                    except:
                        break
            
            monitor_thread = threading.Thread(target=monitor_system, daemon=True)
            monitor_thread.start()
            
            # Crée la liste des fichiers pour ffmpeg
            file_list = self.temp_dir / "filelist.txt"
            with open(file_list, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file.absolute()}'\n")
            
            # Configuration
            config = getattr(self, 'config', ProcessingConfig())
            max_threads = os.cpu_count() or 24
            use_cuda = self.detect_cuda_support()
            
            # Métadonnées
            metadata_dict = metadata.get_metadata_dict()
            metadata_args = []
            for key, value in metadata_dict.items():
                metadata_args.extend(['-metadata', f'{key}={value}'])
            
            # Commande FFmpeg optimisée AAC
            if use_cuda and config.enable_aac_optimization:
                logger.info("🚀 UTILISATION CUDA RTX 4070 - AAC PARALLÈLE OPTIMISÉ")
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(file_list),
                    # Multi-threading CPU maximum pour encodeur AAC
                    '-threads', str(max_threads),
                    '-thread_type', 'slice',
                    # Filtres audio optimisés pour AAC
                    '-c:a', 'aac',
                    '-b:a', config.audio_bitrate,
                    '-ac', str(config.audio_channels),
                    '-ar', str(config.sample_rate),
                    # Optimisations AAC spécifiques
                    '-aac_coder', config.aac_coder,
                    '-cutoff', str(config.cutoff_freq),
                    '-profile:a', config.aac_profile,
                    # CBR pour taille prévisible et compression maximale
                    '-vbr', '0',  # CBR mode
                    # Optimisations mémoire et cache
                    '-bufsize', '16M',  # Buffer plus petit pour compression
                    '-maxrate', config.audio_bitrate,
                    # Paramètres conteneur M4B optimisé
                    '-movflags', '+faststart',
                    # Métadonnées
                    *metadata_args,
                    '-progress', 'pipe:1',
                    '-f', 'mp4',  # Conteneur MP4 pour M4B
                    str(output_path)
                ]
                codec_info = f"AAC CBR64k + CUDA RTX 4070 + {max_threads} threads"
            elif use_cuda:
                logger.info("🚀 UTILISATION GPU NVIDIA RTX 4070 - AAC FILTRES ACCÉLÉRÉS")
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(file_list),
                    # Multi-threading CPU maximum
                    '-threads', str(max_threads),
                    '-thread_type', 'slice',
                    # Filtres audio avec accélération GPU
                    '-c:a', 'aac',
                    '-b:a', config.audio_bitrate,
                    '-ac', str(config.audio_channels),
                    '-ar', str(config.sample_rate),
                    # Optimisations AAC
                    '-aac_coder', config.aac_coder,
                    '-cutoff', str(config.cutoff_freq),
                    '-profile:a', config.aac_profile,
                    '-vbr', '0',
                    # Optimisations mémoire
                    '-bufsize', '16M',
                    '-maxrate', config.audio_bitrate,
                    # Paramètres
                    '-movflags', '+faststart',
                    # Métadonnées
                    *metadata_args,
                    '-progress', 'pipe:1',
                    '-f', 'mp4',
                    str(output_path)
                ]
                codec_info = f"AAC CBR64k + GPU RTX 4070 + {max_threads} threads"
            else:
                logger.info(f"⚙️ UTILISATION CPU AAC HAUTE QUALITÉ - {max_threads} threads")
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(file_list),
                    # Multi-threading CPU maximum
                    '-threads', str(max_threads),
                    '-thread_type', 'slice',
                    # AAC HAUTE QUALITÉ CPU
                    '-c:a', 'aac',
                    '-b:a', config.audio_bitrate,
                    '-ac', str(config.audio_channels),
                    '-ar', str(config.sample_rate),
                    # Optimisations AAC complètes
                    '-aac_coder', config.aac_coder,
                    '-cutoff', str(config.cutoff_freq),
                    '-profile:a', config.aac_profile,
                    '-vbr', '0',
                    # Optimisations mémoire
                    '-bufsize', '16M',
                    '-maxrate', config.audio_bitrate,
                    # Paramètres
                    '-movflags', '+faststart',
                    # Métadonnées
                    *metadata_args,
                    '-progress', 'pipe:1',
                    '-f', 'mp4',
                    str(output_path)
                ]
                codec_info = f"AAC CBR64k + CPU {max_threads} threads"
            
            # Calcul détaillé de la taille avec debug
            total_input_size = 0
            logger.info(f"🔍 DEBUG: Analyse des {len(audio_files)} fichiers audio:")
            for i, f in enumerate(audio_files):
                size_mb = f.stat().st_size / (1024*1024)
                total_input_size += f.stat().st_size
                logger.info(f"   {i+1:2d}. {f.name} = {size_mb:.1f}MB")
            
            total_input_mb = total_input_size / (1024*1024)
            logger.info(f'📊 Taille source calculée: {total_input_mb:.1f}MB ({len(audio_files)} fichiers)')
            logger.info(f'📊 Taille attendue: ~{total_input_mb * 0.3:.1f}MB (compression ~70%)')
            
            # Lance FFmpeg
            logger.info("🚀 LANCEMENT FFmpeg...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            # Suivi de progression avec timeout et détection taille maximale
            start_time = time.time()
            last_size = 0
            last_stats_time = 0
            timeout = 7200  # 2 heures max pour gros audiobooks
            max_output_size = total_input_mb * 1.5  # Taille maximale autorisée (150% de l'entrée)
            
            while True:
                if process.poll() is not None:
                    break
                
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Timeout de sécurité
                if elapsed > timeout:
                    logger.error(f"❌ TIMEOUT après {timeout/60:.0f} minutes")
                    process.terminate()
                    break
                
                # Vérification taille maximale pour éviter boucle infinie
                if output_path.exists():
                    current_size_mb = output_path.stat().st_size / (1024*1024)
                    if current_size_mb > max_output_size:
                        logger.error(f"❌ TAILLE EXCESSIVE: {current_size_mb:.1f}MB > {max_output_size:.1f}MB - BOUCLE INFINIE DÉTECTÉE")
                        process.terminate()
                        break
                
                # Stats système toutes les 10 secondes
                if (current_time - last_stats_time) > 10:
                    cpu = system_stats['cpu_percent']
                    ram = system_stats['ram_mb']
                    
                    if output_path.exists():
                        data = output_path.stat().st_size / (1024*1024)
                        progress_percent = min(100, (data / total_input_mb) * 100)
                        
                        # Calcul vitesse et ETA
                        if elapsed > 30 and data > 1:  # Attend 30s avant calcul
                            speed_mbps = data / (elapsed / 60)  # MB/min
                            if speed_mbps > 0:
                                eta_minutes = (total_input_mb - data) / speed_mbps
                                eta_hours = int(eta_minutes // 60)
                                eta_mins = int(eta_minutes % 60)
                                eta_str = f"{eta_hours:02d}h{eta_mins:02d}mn"
                            else:
                                eta_str = "--h--mn"
                            
                            speed_str = f"{speed_mbps:.1f}MB/min"
                        else:
                            data = 0
                            progress_percent = 0
                            speed_str = "--"
                            eta_str = "--h--mn"
                        
                        # Barre de progression
                        bar_length = 30
                        filled = int(bar_length * progress_percent / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        
                        logger.info(f"📊 [{bar}] {progress_percent:3.0f}% | {data:6.1f}MB/{total_input_mb:.1f}MB | {speed_str} | ETA {eta_str}")
                        last_stats_time = current_time
                
                time.sleep(0.5)  # Pause plus courte pour réactivité
            
            # Arrêt surveillance et nettoyage mémoire
            stop_monitoring.set()
            monitor_thread.join(timeout=2)
            
            # Force l'arrêt du processus FFmpeg s'il est encore actif
            if process.poll() is None:
                logger.warning("🔄 Force arrêt processus FFmpeg...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.error("💥 Force KILL processus FFmpeg...")
                    process.kill()
                    process.wait()
            
            # Nettoyage mémoire agressif
            gc.collect()
            logger.info("🧹 Nettoyage mémoire effectué")
            
            # Attend la fin
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f'❌ Erreur FFmpeg: {stderr}')
                return False
            
            # Statistiques finales
            total_time = time.time() - start_time
            input_size = sum(f.stat().st_size for f in audio_files) / (1024*1024)
            output_size = output_path.stat().st_size / (1024*1024) if output_path.exists() else 0
            
            logger.info(f"✅ Conversion terminée en {total_time//60:.0f}m{total_time%60:.0f}s")
            logger.info(f"📊 Qualité: {codec_info} | {config.audio_bitrate} | {config.audio_channels} canaux | {config.sample_rate}Hz")
            logger.info(f"📊 Compression M4B: {input_size:.1f}MB → {output_size:.1f}MB ({((1-output_size/input_size)*100):.1f}% - optimisé AAC)")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Erreur conversion M4B: {e}")
            return False
    
    def process_audiobook(self, file_path: Path) -> bool:
        """Traite un fichier audiobook complet"""
        try:
            logger.info(f"🚀 TRAITEMENT: {file_path.name}")
            
            # 1. Métadonnées
            metadata = self.parse_filename(file_path.name)
            logger.info(f"   ✅ Auteur: {metadata.author}")
            logger.info(f"   ✅ Titre: {metadata.title}")
            
            # 2. Dossier de travail
            work_dir = self.temp_dir / file_path.stem
            work_dir.mkdir(exist_ok=True)
            
            # 3. Recherche fichiers audio
            if file_path.is_file() and file_path.suffix.lower() in ['.zip', '.rar']:
                logger.info(f"   📦 Extraction archive...")
                if not self.extract_archive(file_path, work_dir):
                    return False
                audio_files = self.find_audio_files(work_dir)
            elif file_path.is_dir():
                audio_files = self.find_audio_files(file_path)
            else:
                audio_files = [file_path]
            
            if not audio_files:
                logger.error(f"❌ Aucun fichier audio trouvé")
                return False
            
            logger.info(f"   ✅ {len(audio_files)} fichiers audio")
            
            # 4. Traitement selon le mode
            config = getattr(self, 'config', ProcessingConfig())
            
            if config.processing_mode == "concat_fast":
                # Phase 1: Concaténation 1:1 rapide
                logger.info("🔄 Phase 1: Concaténation 1:1 rapide...")
                output_filename = f"{metadata.get_filename_format()}.m4b"
                output_path = self.output_dir / output_filename
                
                success = self.concat_fast_m4b(audio_files, output_path, metadata)
                
            elif config.processing_mode == "encode_aac":
                # Phase 2: Réencodage AAC individuel
                logger.info("🔄 Phase 2: Réencodage AAC individuel...")
                output_filename = f"{metadata.get_filename_format()}.m4b"
                output_path = self.output_dir / output_filename
                
                success = self.convert_to_m4b(audio_files, output_path, metadata)
                
            else:
                # Phase 3: M4B final (par défaut)
                logger.info("🔄 Phase 3: M4B final optimisé...")
                output_filename = f"{metadata.get_filename_format()}.m4b"
                output_path = self.output_dir / output_filename
                
                success = self.convert_to_m4b(audio_files, output_path, metadata)
            
            if success:
                logger.info(f"✅ SUCCÈS: {output_filename}")
                return True
            else:
                logger.error(f"❌ ÉCHEC: {file_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"💥 ERREUR: {e}")
            return False
        finally:
            # Nettoyage
            if 'work_dir' in locals() and work_dir.exists():
                shutil.rmtree(work_dir)
    
    def process_all(self) -> Dict[str, int]:
        """Traite tous les audiobooks"""
        logger.info("🚀 TRAITEMENT GLOBAL")
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        self.output_dir.mkdir(exist_ok=True)
        
        # Analyse
        all_items = list(self.source_dir.iterdir())
        files_to_process = []
        folders_to_process = []
        
        for item in all_items:
            if item.is_file() and item.suffix.lower() in ['.zip', '.rar', '.mp3', '.m4a', '.m4b']:
                files_to_process.append(item)
            elif item.is_dir():
                audio_count = len(self.find_audio_files(item))
                if audio_count > 0:
                    folders_to_process.append(item)
        
        total_to_process = len(files_to_process) + len(folders_to_process)
        logger.info(f"📋 Fichiers: {len(files_to_process)}, Dossiers: {len(folders_to_process)}, Total: {total_to_process}")
        
        # Traitement
        for i, folder_path in enumerate(folders_to_process, 1):
            logger.info(f"\n📂 DOSSIER {i}/{len(folders_to_process)}: {folder_path.name}")
            if self.process_audiobook(folder_path):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        for i, file_path in enumerate(files_to_process, 1):
            logger.info(f"\n📃 FICHIER {i}/{len(files_to_process)}: {file_path.name}")
            if self.process_audiobook(file_path):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        # Résultats
        logger.info("\n🏁 TRAITEMENT TERMINÉ")
        logger.info(f"✅ Succès: {results['success']}")
        logger.info(f"❌ Échecs: {results['failed']}")
        logger.info(f"📁 Fichiers dans: {self.output_dir}")
        
        return results

if __name__ == "__main__":
    # Test
    SOURCE_DIR = "/home/fabrice/Documents/Audiobooks"
    OUTPUT_DIR = "/home/fabrice/Documents/Projets/scripts_audiobooks/test_audio"
    TEMP_DIR = "/tmp/audiobooks"
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    processor = AudiobookProcessor(SOURCE_DIR, OUTPUT_DIR, TEMP_DIR)
    results = processor.process_all()
    
    print(f"\n📊 Résultats: Succès {results['success']}, Échecs {results['failed']}")
