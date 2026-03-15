"""
🔄 Module de Synchronisation Audiobookshelf - Audiobook Manager Pro
Intégration de la synchronisation avec Audiobookshelf dans le processeur principal
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from integrations.audiobookshelf_client import (
    AudiobookshelfClient, 
    AudiobookshelfSyncManager,
    AudiobookshelfConfig,
    create_audiobookshelf_client,
    create_sync_manager
)
from core.processor import AudiobookMetadata
from plugins.exports import AudiobookshelfExportPlugin

logger = logging.getLogger(__name__)

@dataclass
class SyncConfig:
    """Configuration de synchronisation"""
    enabled: bool = False
    auto_sync: bool = False
    library_id: Optional[str] = None
    upload_after_conversion: bool = True
    conflict_resolution: str = "skip"  # skip, overwrite, merge
    batch_size: int = 10
    retry_failed_uploads: bool = True
    max_retry_attempts: int = 3

class AudiobookshelfIntegration:
    """Intégration d'Audiobookshelf avec le processeur principal"""
    
    def __init__(self, sync_config: SyncConfig, abs_config: AudiobookshelfConfig):
        self.sync_config = sync_config
        self.abs_config = abs_config
        self.client = None
        self.sync_manager = None
        self.is_connected = False
        
    def initialize(self) -> bool:
        """Initialiser la connexion à Audiobookshelf"""
        if not self.sync_config.enabled:
            logger.info("🔄 Synchronisation Audiobookshelf désactivée")
            return True
            
        logger.info("🔄 Initialisation de la synchronisation Audiobookshelf...")
        
        try:
            # Création du client
            self.client = create_audiobookshelf_client(self.abs_config)
            self.sync_manager = create_sync_manager(self.client)
            
            # Test de connexion
            if self.client.test_connection():
                # Authentification
                if self.client.authenticate():
                    self.is_connected = True
                    logger.info("✅ Synchronisation Audiobookshelf initialisée")
                    return True
                else:
                    logger.error("❌ Échec de l'authentification Audiobookshelf")
                    return False
            else:
                logger.error("❌ Impossible de se connecter à Audiobookshelf")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            return False
            
    def sync_audiobook(self, audiobook_path: Path, metadata: AudiobookMetadata) -> Dict[str, Any]:
        """Synchroniser un audiobook avec Audiobookshelf"""
        if not self.is_connected:
            logger.warning("⚠️ Audiobookshelf non connecté, synchronisation ignorée")
            return {'success': False, 'error': 'Not connected'}
            
        logger.info(f"🔄 Synchronisation de l'audiobook: {audiobook_path.name}")
        
        try:
            # Conversion des métadonnées pour Audiobookshelf
            abs_metadata = self._convert_metadata_for_abs(metadata)
            
            # Upload via plugin d'export
            export_plugin = AudiobookshelfExportPlugin(self.client, self.sync_config.library_id)
            success = export_plugin.export(audiobook_path, abs_metadata)

            if success:
                logger.info(f"✅ Audiobook synchronisé: {audiobook_path.name}")
                return {
                    'success': True,
                    'item_id': None,
                    'message': 'Upload réussi'
                }
            else:
                logger.error("❌ Échec de l'upload")
                return {
                    'success': False,
                    'error': 'Upload failed'
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la synchronisation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def sync_directory(self, directory: Path) -> Dict[str, Any]:
        """Synchroniser un répertoire complet"""
        if not self.is_connected:
            logger.warning("⚠️ Audiobookshelf non connecté, synchronisation ignorée")
            return {'success': False, 'error': 'Not connected'}
            
        logger.info(f"🔄 Synchronisation du répertoire: {directory}")
        
        try:
            result = self.sync_manager.sync_directory(
                directory, 
                self.sync_config.library_id,
                recursive=True
            )
            
            uploaded = result.get('stats', {}).get('uploaded_files', 0)
            logger.info(f"✅ Synchronisation terminée: {uploaded} fichiers uploadés")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la synchronisation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def check_existing_item(self, title: str, author: str = "") -> Optional[Dict[str, Any]]:
        """Vérifier si un élément existe déjà"""
        if not self.is_connected:
            return None
            
        query = f"{title}"
        if author:
            query += f" {author}"
            
        items = self.client.search_items(query, self.sync_config.library_id)
        return items[0] if items else None
        
    def update_item_metadata(self, item_id: str, metadata: AudiobookMetadata) -> bool:
        """Mettre à jour les métadonnées d'un élément"""
        if not self.is_connected:
            return False
            
        try:
            abs_metadata = self._convert_metadata_for_abs(metadata)
            result = self.client.update_metadata(item_id, abs_metadata)
            
            if result:
                logger.info(f"✅ Métadonnées mises à jour: {item_id}")
                return True
            else:
                logger.error(f"❌ Échec de la mise à jour: {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour: {e}")
            return False
            
    def get_libraries(self) -> List[Dict[str, Any]]:
        """Récupérer la liste des bibliothèques"""
        if not self.is_connected:
            return []
            
        try:
            libraries = self.client.get_libraries()
            logger.info(f"📚 {len(libraries)} bibliothèques trouvées")
            return libraries
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des bibliothèques: {e}")
            return []
            
    def create_library(self, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """Créer une nouvelle bibliothèque"""
        if not self.is_connected:
            return None
            
        try:
            result = self.client.create_library(name, description)
            if result:
                logger.info(f"✅ Bibliothèque créée: {name}")
                return result
            else:
                logger.error(f"❌ Échec de la création de la bibliothèque: {name}")
                return None
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de la bibliothèque: {e}")
            return None
            
    def _convert_metadata_for_abs(self, metadata: AudiobookMetadata) -> Dict[str, Any]:
        """Convertir les métadonnées pour Audiobookshelf"""
        year = getattr(metadata, 'year', None)
        published_year = int(year) if isinstance(year, str) and year.isdigit() else year

        return {
            'title': getattr(metadata, 'title', ''),
            'author': getattr(metadata, 'author', ''),
            'series': getattr(metadata, 'series', None),
            'series_part': getattr(metadata, 'series_number', None),
            'description': getattr(metadata, 'description', None),
            'narrator': getattr(metadata, 'narrator', None),
            'publisher': getattr(metadata, 'publisher', None),
            'published_year': published_year,
            'language': getattr(metadata, 'language', 'fr'),
            'duration': getattr(metadata, 'duration', None),
            'file_format': getattr(metadata, 'file_format', 'm4b'),
            'bitrate': getattr(metadata, 'bitrate', None),
            'sample_rate': getattr(metadata, 'sample_rate', None),
            'chapters': metadata.chapters if hasattr(metadata, 'chapters') else [],
            'tags': metadata.tags if hasattr(metadata, 'tags') else []
        }
        
    def get_sync_status(self) -> Dict[str, Any]:
        """Obtenir le statut de synchronisation"""
        return {
            'enabled': self.sync_config.enabled,
            'connected': self.is_connected,
            'auto_sync': self.sync_config.auto_sync,
            'library_id': self.sync_config.library_id,
            'last_sync': getattr(self.sync_manager, 'last_sync_time', None) if self.sync_manager else None,
            'stats': getattr(self.sync_manager, 'sync_stats', {}) if self.sync_manager else {}
        }
        
    def disconnect(self):
        """Déconnecter d'Audiobookshelf"""
        if self.client:
            self.client.token = None
            self.is_connected = False
            logger.info("🔄 Déconnecté d'Audiobookshelf")

class SyncManager:
    """Gestionnaire principal de synchronisation"""
    
    def __init__(self):
        self.integration = None
        self.sync_config = SyncConfig()
        self.abs_config = AudiobookshelfConfig()
        
    def configure(self, sync_config: SyncConfig, abs_config: AudiobookshelfConfig):
        """Configurer la synchronisation"""
        self.sync_config = sync_config
        self.abs_config = abs_config
        
        # Création de l'intégration
        self.integration = AudiobookshelfIntegration(sync_config, abs_config)
        
    def initialize(self) -> bool:
        """Initialiser la synchronisation"""
        if self.integration:
            return self.integration.initialize()
        return False
        
    def sync_audiobook(self, audiobook_path: Path, metadata: AudiobookMetadata) -> Dict[str, Any]:
        """Synchroniser un audiobook"""
        if self.integration:
            return self.integration.sync_audiobook(audiobook_path, metadata)
        return {'success': False, 'error': 'Not initialized'}
        
    def sync_directory(self, directory: Path) -> Dict[str, Any]:
        """Synchroniser un répertoire"""
        if self.integration:
            return self.integration.sync_directory(directory)
        return {'success': False, 'error': 'Not initialized'}
        
    def get_status(self) -> Dict[str, Any]:
        """Obtenir le statut"""
        if self.integration:
            return self.integration.get_sync_status()
        return {'enabled': False, 'connected': False}
        
    def disconnect(self):
        """Déconnecter"""
        if self.integration:
            self.integration.disconnect()

# Instance globale du gestionnaire
sync_manager = SyncManager()

def configure_sync(sync_config: SyncConfig, abs_config: AudiobookshelfConfig):
    """Configurer la synchronisation globale"""
    sync_manager.configure(sync_config, abs_config)
    
def initialize_sync() -> bool:
    """Initialiser la synchronisation globale"""
    return sync_manager.initialize()
    
def sync_audiobook(audiobook_path: Path, metadata: AudiobookMetadata) -> Dict[str, Any]:
    """Synchroniser un audiobook avec la configuration globale"""
    return sync_manager.sync_audiobook(audiobook_path, metadata)
    
def sync_directory(directory: Path) -> Dict[str, Any]:
    """Synchroniser un répertoire avec la configuration globale"""
    return sync_manager.sync_directory(directory)
    
def get_sync_status() -> Dict[str, Any]:
    """Obtenir le statut de synchronisation global"""
    return sync_manager.get_status()
    
def disconnect_sync():
    """Déconnecter la synchronisation globale"""
    sync_manager.disconnect()
