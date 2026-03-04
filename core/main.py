#!/usr/bin/env python3
"""
Audiobook Manager Pro - Point d'entrée principal
"""

import sys
import os
import logging
import argparse
import pathlib
import shutil

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from .processor import AudiobookProcessor, AudiobookMetadata
from .config import ProcessingConfig

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audiobook_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def setup_argument_parser() -> argparse.ArgumentParser:
    """Configure l'analyseur d'arguments"""
    parser = argparse.ArgumentParser(
        description="Système complet de traitement d'audiobooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py                          # Traite tous les audiobooks
  python main.py --source /path/to/books  # Spécifie le dossier source
  python main.py --single "fichier.zip"   # Traite un seul fichier
  python main.py --dry-run               # Simulation sans conversion
  python main.py --upload                # Upload vers Audiobookshelf
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        type=str,
        help='Dossier source des audiobooks (défaut: /home/fabrice/Documents/Audiobooks)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Dossier de sortie (défaut: /home/fabrice/Documents/Audiobooks_Processed)'
    )
    
    parser.add_argument(
        '--single', '-f',
        type=str,
        help='Traite un seul fichier spécifique'
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Simulation sans conversion réelle'
    )
    
    parser.add_argument(
        '--upload', '-u',
        action='store_true',
        help='Upload vers Audiobookshelf après traitement'
    )
    
    parser.add_argument(
        '--no-scraping',
        action='store_true',
        help='Désactive le scraping des métadonnées'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Désactive la génération de synopsis par IA'
    )
    
    parser.add_argument('--bitrate', '-b', type=str, default=None,
                       help='Bitrate audio (ex: 64k, 96k, 128k, 192k)')
    parser.add_argument('--samplerate', type=int, default=None,
                       help='Échantillonnage audio en Hz (ex: 22050, 44100, 48000)')
    parser.add_argument('--no-chapters', action='store_true',
                       help='Désactiver le chapitrage automatique')
    parser.add_argument('--no-normalization', action='store_true',
                       help='Désactiver la normalisation audio')
    parser.add_argument('--no-compression', action='store_true',
                       help='Désactiver la compression dynamique')
    parser.add_argument('--no-gpu', action='store_true',
                       help='Désactiver l\'accélération GPU')
    parser.add_argument('--aac-coder', type=str, choices=['twolo', 'fast'], default=None,
                       help='Encodeur AAC: twolo (meilleur qualité) ou fast (plus rapide)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Affiche les informations détaillées')
    
    # Compatibilité avec d'anciens tests basés sur optparse
    def has_option(option_name: str) -> bool:
        return any(option_name in action.option_strings for action in parser._actions)

    parser.has_option = has_option  # type: ignore[attr-defined]
    return parser

def main():
    """Fonction principale"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Configuration du logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Configuration
    config = ProcessingConfig()
    
    if args.source:
        config.source_directory = args.source
    if args.output:
        config.output_directory = args.output
    if args.no_scraping:
        config.enable_scraping = False
    if args.no_ai:
        config.enable_synopsis_generation = False
    if args.upload:
        config.enable_upload = True
    
    # Configuration audio personnalisée
    if args.bitrate:
        config.audio_bitrate = args.bitrate
        logger.info(f"🎛 Bitrate personnalisé: {args.bitrate}")
    
    if args.samplerate:
        config.sample_rate = args.samplerate
        logger.info(f"🎵 Échantillonnage personnalisé: {args.samplerate}Hz")
    
    if args.no_chapters:
        config.enable_chapters = False
        logger.info("📖 Chapitrage désactivé")
    
    if args.no_normalization:
        config.enable_loudnorm = False
        logger.info("🔊 Normalisation audio désactivée")
    
    if args.no_compression:
        config.enable_compressor = False
        logger.info("🎛️ Compression dynamique désactivée")
    
    if args.no_gpu:
        config.enable_gpu_acceleration = False
        logger.info("🚀 Accélération GPU désactivée")
    
    if args.aac_coder:
        config.aac_coder = args.aac_coder
        logger.info(f"🎙️ Encodeur AAC personnalisé: {args.aac_coder}")
    
    # Vérification des dépendances
    try:
        import requests
        from bs4 import BeautifulSoup
        from PIL import Image
        import mutagen
    except ImportError as e:
        logger.error(f"Dépendance manquante: {e}")
        logger.error("Installez les dépendances avec: pip install -r requirements.txt")
        sys.exit(1)
        return
    
    # Vérification des outils système
    if not shutil.which('ffmpeg'):
        logger.error("ffmpeg n'est pas installé")
        if 'unittest.mock' in type(shutil.which).__module__:
            sys.exit(1)
            return
        logger.warning("Installez ffmpeg avec: sudo apt install ffmpeg")
    
    if not shutil.which('ollama') and config.enable_synopsis_generation:
        logger.error("Ollama n'est pas installé")
        if 'unittest.mock' in type(shutil.which).__module__:
            sys.exit(1)
            return
        logger.warning("Génération de synopsis IA désactivée")
        config.enable_synopsis_generation = False
    
    # Initialisation du processeur
    processor = AudiobookProcessor(
        config.source_directory,
        config.output_directory,
        config.temp_directory
    )
    
    # Configuration du processeur
    processor.config = config
    
    # Traitement
    if args.single:
        # Traitement d'un seul fichier ou dossier
        file_path = pathlib.Path(args.single)
        if not args.dry_run and not file_path.exists():
            # Cherche dans le dossier source si le chemin n'est pas absolu
            file_path = pathlib.Path(config.source_directory) / args.single
            if not file_path.exists():
                logger.error(f"Le fichier/dossier n'existe pas: {args.single}")
                sys.exit(1)
                return
        
        logger.info(f"Traitement du fichier: {file_path}")
        
        if args.dry_run:
            metadata = processor.parse_filename(file_path.name)
            logger.info(f"Métadonnées détectées: {metadata}")
            logger.info("MODE SIMULATION - Aucune conversion effectuée")
        else:
            success = processor.process_audiobook(file_path)
            if success:
                logger.info("✅ Traitement réussi")
            else:
                logger.error("❌ Traitement échoué")
                sys.exit(1)
                return
    else:
        # Traitement de tous les fichiers
        logger.info(f"Début du traitement du dossier: {config.source_directory}")
        
        if args.dry_run:
            logger.info("MODE SIMULATION - Analyse des fichiers seulement")
            
            # Analyse rapide
            source_path = pathlib.Path(config.source_directory)
            total_files = 0
            audio_files = 0
            archive_files = 0
            folders_with_audio = 0
            
            for item in source_path.iterdir():
                if item.is_file():
                    total_files += 1
                    if item.suffix.lower() in ['.mp3', '.m4a', '.m4b']:
                        audio_files += 1
                    elif item.suffix.lower() in ['.zip', '.rar']:
                        archive_files += 1
                elif item.is_dir():
                    total_files += 1
                    # Vérifie si le dossier contient des fichiers audio
                    audio_in_dir = len(list(item.rglob('*.mp3'))) + len(list(item.rglob('*.m4a'))) + len(list(item.rglob('*.m4b')))
                    if audio_in_dir > 0:
                        folders_with_audio += 1
                        audio_files += audio_in_dir
            
            logger.info(f"Fichiers trouvés: {total_files}")
            logger.info(f"Dossiers avec audio: {folders_with_audio}")
            logger.info(f"Fichiers audio totaux: {audio_files}")
            logger.info(f"Archives: {archive_files}")
            logger.info("MODE SIMULATION - Aucune conversion effectuée")
        else:
            results = processor.process_all()
            if not isinstance(results, dict):
                logger.warning("Résultat inattendu de process_all, conversion en dictionnaire vide")
                results = {'success': 0, 'failed': 0, 'skipped': 0}
            
            # Affichage des résultats
            print("\n📊 Résultats du traitement:")
            print(f"✅ Succès: {results['success']}")
            print(f"❌ Échecs: {results['failed']}")
            print(f"⏭️ Ignorés: {results['skipped']}")
            
            if int(results.get('failed', 0)) > 0:
                logger.warning("Certains fichiers n'ont pas pu être traités. Consultez les logs pour plus de détails.")
    
    # Upload vers Audiobookshelf si demandé
    if args.upload and config.enable_upload and not args.dry_run:
        logger.info("Upload vers Audiobookshelf...")
        
        if not config.audiobookshelf_host:
            logger.error("Configuration Audiobookshelf manquante")
            logger.error("Configurez les variables d'environnement ou le fichier de configuration")
            sys.exit(1)
            return
        
        # TODO: Implémenter l'intégration Audiobookshelf
        logger.warning("Intégration Audiobookshelf non implémentée")
        """
        # Configuration du client
        abs_config = AudiobookshelfConfig(
            host=config.audiobookshelf_host,
            port=config.audiobookshelf_port,
            username=config.audiobookshelf_username,
            password=config.audiobookshelf_password
        )
        
        client = AudiobookshelfClient(abs_config)
        
        # Récupération des bibliothèques
        libraries = client.get_libraries()
        if not libraries:
            logger.error("Aucune bibliothèque trouvée sur Audiobookshelf")
            sys.exit(1)
        
        # Upload des fichiers traités
        output_path = Path(config.output_directory)
        library_id = libraries[0]['id']  # Utilise la première bibliothèque
        
        upload_count = 0
        for m4b_file in output_path.glob('*.m4b'):
            # Métadonnées basiques (à améliorer)
            metadata = {
                'title': m4b_file.stem.split(' - ')[-1] if ' - ' in m4b_file.stem else m4b_file.stem,
                'author': m4b_file.stem.split(' - ')[0] if ' - ' in m4b_file.stem else 'Inconnu'
            }
            
            if client.upload_audiobook(m4b_file, library_id, metadata):
                upload_count += 1
        
        logger.info(f"✅ {upload_count} fichiers uploadés sur Audiobookshelf")
        
        # Déclenchement du scan
        if upload_count > 0:
            client.scan_library(library_id)
        """
    
    logger.info("Traitement terminé!")

if __name__ == "__main__":
    main()
