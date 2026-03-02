#!/usr/bin/env python3
"""
Audiobook Manager Pro - Point d'entrée principal
Gère la nouvelle structure src/ et logs/
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Importer les modules depuis src/
from audiobook_processor import AudiobookProcessor, AudiobookMetadata
from config import ProcessingConfig
from audiobookshelf_client import AudiobookshelfClient, AudiobookshelfConfig
from scraper import BookScraper

def main():
    """Point d'entrée principal pour l'application CLI"""
    import argparse
    import logging
    
    # Configuration du logging vers logs/
    log_file = Path(__file__).parent / "logs" / "audiobook_processing.log"
    log_file.parent.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description='Audiobook Manager Pro - Conversion et gestion d\'audiobooks')
    parser.add_argument('--source', required=True, help='Répertoire source contenant les audiobooks')
    parser.add_argument('--output', required=True, help='Répertoire de sortie pour les fichiers M4B')
    parser.add_argument('--bitrate', default='128k', help='Bitrate audio (64k, 96k, 128k, 192k)')
    parser.add_argument('--gpu', action='store_true', help='Utiliser l\'accélération GPU si disponible')
    parser.add_argument('--verbose', action='store_true', help='Mode verbeux')
    
    args = parser.parse_args()
    
    try:
        # Configuration
        config = ProcessingConfig(
            source_directory=args.source,
            output_directory=args.output,
            audio_bitrate=args.bitrate,
            enable_gpu_acceleration=args.gpu,
            sample_rate=44100 if "44k" in args.output else 48000
        )
        
        # Traitement
        processor = AudiobookProcessor(
            source_dir=args.source,
            output_dir=args.output,
            temp_dir="/tmp/audiobooks"
        )
        
        logger.info(f"🎧 Démarrage traitement de: {args.source}")
        logger.info(f"📁 Sortie vers: {args.output}")
        logger.info(f"🎵 Bitrate: {args.bitrate}")
        logger.info(f"🚀 GPU: {'Activé' if args.gpu else 'Désactivé'}")
        
        # Lister et traiter les fichiers
        source_path = Path(args.source)
        audio_files = []
        
        # Support des fichiers directs
        if source_path.is_file() and source_path.suffix.lower() in ['.mp3', '.m4a', '.wav', '.flac']:
            audio_files = [source_path]
        # Support des dossiers
        elif source_path.is_dir():
            for ext in ['*.mp3', '*.m4a', '*.wav', '*.flac']:
                audio_files.extend(source_path.glob(ext))
            # Support des archives
            for archive_ext in ['*.zip', '*.rar']:
                for archive in source_path.glob(archive_ext):
                    logger.info(f"📦 Archive détectée: {archive}")
                    # TODO: Implémenter extraction d'archives
        else:
            logger.error(f"❌ Format non supporté: {source_path}")
            return 1
        
        if not audio_files:
            logger.warning("⚠️ Aucun fichier audio trouvé")
            return 0
        
        logger.info(f"📊 {len(audio_files)} fichier(s) à traiter")
        
        # Trier les fichiers par ordre alphabétique
        audio_files.sort()
        
        # Créer les métadonnées à partir du premier fichier
        metadata = processor.parse_filename(audio_files[0].name)
        
        # Créer le chemin de sortie
        output_file = Path(args.output) / f"{metadata.title}.m4b"
        
        # Configurer le bitrate et sample rate
        processor.config = ProcessingConfig(
            audio_bitrate=args.bitrate,
            sample_rate=44100 if "44k" in args.output else 48000,
            enable_gpu_acceleration=args.gpu
        )
        
        # Convertir tous les fichiers en un seul M4B
        success = processor.convert_to_m4b(audio_files, output_file, metadata)
        
        if success:
            logger.info(f"✅ Conversion réussie: {output_file.name}")
            return 0
        else:
            logger.error(f"❌ Échec conversion")
            return 1
        
    except KeyboardInterrupt:
        logger.info("⏹️ Interruption utilisateur")
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
