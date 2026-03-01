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
            source_dir=Path(args.source),
            output_dir=Path(args.output),
            bitrate=args.bitrate,
            enable_gpu=args.gpu,
            verbose=args.verbose
        )
        
        # Traitement
        processor = AudiobookProcessor(config)
        
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
        
        # Traiter chaque fichier
        success_count = 0
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"🎵 Fichier {i}/{len(audio_files)}: {audio_file.name}")
            
            try:
                # Parser le nom de fichier pour métadonnées
                metadata = processor.parse_filename(audio_file.name)
                
                # Créer le chemin de sortie
                output_file = Path(args.output) / f"{metadata.title}.m4b"
                
                # Convertir
                success = processor.convert_to_m4b(audio_file, output_file)
                
                if success:
                    success_count += 1
                    logger.info(f"✅ Conversion réussie: {output_file.name}")
                else:
                    logger.error(f"❌ Échec conversion: {audio_file.name}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur traitement {audio_file.name}: {e}")
                continue
        
        logger.info(f"🎉 Traitement terminé: {success_count}/{len(audio_files)} succès")
        return 0 if success_count > 0 else 1
        
    except KeyboardInterrupt:
        logger.info("⏹️ Interruption utilisateur")
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
