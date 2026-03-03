"""
🔗 Client Audiobookshelf API - Audiobook Manager Pro
Interface pour la synchronisation avec Audiobookshelf
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AudiobookshelfConfig:
    """Configuration pour la connexion Audiobookshelf"""
    host: str = "localhost"
    port: int = 13378
    username: str = ""
    password: str = ""
    use_ssl: bool = False
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class AudiobookshelfClient:
    """Client API pour Audiobookshelf"""
    
    def __init__(self, config: AudiobookshelfConfig):
        self.config = config
        self.session = requests.Session()
        self.token = None
        self.base_url = self._build_base_url()
        
        # Configuration du session
        self.session.timeout = config.timeout
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AudiobookManagerPro/2.0.0'
        })
        
    def _build_base_url(self) -> str:
        """Construire l'URL de base de l'API"""
        protocol = "https" if self.config.use_ssl else "http"
        return f"{protocol}://{self.config.host}:{self.config.port}"
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Effectuer une requête HTTP avec retry"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentative {attempt + 1}/{self.config.retry_attempts} échouée: {e}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    logger.error(f"Requête échouée après {self.config.retry_attempts} tentatives: {e}")
                    return None
                    
    def authenticate(self) -> bool:
        """Authentifier auprès de Audiobookshelf"""
        logger.info("🔐 Authentification auprès d'Audiobookshelf...")
        
        auth_data = {
            "username": self.config.username,
            "password": self.config.password
        }
        
        result = self._make_request('POST', '/api/login', json=auth_data)
        
        if result and 'user' in result and 'token' in result:
            self.token = result['token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            logger.info(f"✅ Authentifié en tant que {result['user']['username']}")
            return True
        else:
            logger.error("❌ Échec de l'authentification")
            return False
            
    def test_connection(self) -> bool:
        """Tester la connexion à Audiobookshelf"""
        logger.info("🔍 Test de connexion à Audiobookshelf...")
        
        try:
            result = self._make_request('GET', '/api/status')
            if result:
                logger.info("✅ Connexion réussie")
                return True
            else:
                logger.error("❌ Échec de connexion")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur de connexion: {e}")
            return False
            
    def get_libraries(self) -> List[Dict[str, Any]]:
        """Récupérer la liste des bibliothèques"""
        logger.info("📚 Récupération des bibliothèques...")
        
        result = self._make_request('GET', '/api/libraries')
        return result if result else []
        
    def get_library_items(self, library_id: str) -> List[Dict[str, Any]]:
        """Récupérer les éléments d'une bibliothèque"""
        logger.info(f"📚 Récupération des éléments de la bibliothèque {library_id}...")
        
        result = self._make_request('GET', f'/api/libraries/{library_id}/items')
        return result if result else []
        
    def search_items(self, query: str, library_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Rechercher des éléments"""
        logger.info(f"🔍 Recherche: {query}")
        
        params = {'q': query}
        if library_id:
            params['library'] = library_id
            
        result = self._make_request('GET', '/api/search', params=params)
        return result if result else []
        
    def upload_audiobook(self, audiobook_path: Path, metadata: Dict[str, Any], 
                       library_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Uploader un audiobook vers Audiobookshelf"""
        logger.info(f"📤 Upload de l'audiobook: {audiobook_path.name}")
        
        # Vérifier que le fichier existe
        if not audiobook_path.exists():
            logger.error(f"❌ Fichier non trouvé: {audiobook_path}")
            return None
            
        # Préparation des données
        files = {
            'file': (audiobook_path.name, open(audiobook_path, 'rb'), 'audio/m4b')
        }
        
        data = {
            'metadata': json.dumps(metadata),
            'title': metadata.get('title', audiobook_path.stem),
            'author': metadata.get('author', ''),
            'series': metadata.get('series', ''),
            'description': metadata.get('description', ''),
            'duration': metadata.get('duration', 0),
            'size': audiobook_path.stat().st_size
        }
        
        if library_id:
            data['library'] = library_id
            
        try:
            result = self._make_request('POST', '/api/upload', files=files, data=data)
            if result:
                logger.info(f"✅ Upload réussi: {result.get('id', 'unknown')}")
                return result
            else:
                logger.error("❌ Échec de l'upload")
                return None
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'upload: {e}")
            return None
        finally:
            files['file'][1].close()
            
    def update_metadata(self, item_id: str, metadata: Dict[str, Any]) -> bool:
        """Mettre à jour les métadonnées d'un élément"""
        logger.info(f"📝 Mise à jour des métadonnées: {item_id}")
        
        result = self._make_request('PATCH', f'/api/items/{item_id}', json=metadata)
        return result is not None
        
    def get_item_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Récupérer les métadonnées d'un élément"""
        logger.info(f"📋 Récupération des métadonnées: {item_id}")
        
        result = self._make_request('GET', f'/api/items/{item_id}')
        return result
        
    def delete_item(self, item_id: str) -> bool:
        """Supprimer un élément"""
        logger.info(f"🗑️ Suppression de l'élément: {item_id}")
        
        result = self._make_request('DELETE', f'/api/items/{item_id}')
        return result is not None
        
    def create_library(self, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """Créer une nouvelle bibliothèque"""
        logger.info(f"📚 Création de la bibliothèque: {name}")
        
        library_data = {
            'name': name,
            'description': description,
            'mediaType': 'book'
        }
        
        result = self._make_request('POST', '/api/libraries', json=library_data)
        return result
        
    def sync_progress_callback(self, progress: int, message: str):
        """Callback pour la progression de la synchronisation"""
        logger.info(f"🔄 Sync: {progress}% - {message}")

class AudiobookshelfSyncManager:
    """Gestionnaire de synchronisation avec Audiobookshelf"""
    
    def __init__(self, client: AudiobookshelfClient):
        self.client = client
        self.sync_stats = {
            'total_files': 0,
            'uploaded_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'start_time': None,
            'end_time': None
        }
        
    def sync_directory(self, directory: Path, library_id: Optional[str] = None, 
                    recursive: bool = True) -> Dict[str, Any]:
        """Synchroniser un répertoire d'audiobooks"""
        logger.info(f"🔄 Début de la synchronisation: {directory}")
        
        self.sync_stats['start_time'] = time.time()
        
        # Récupération des fichiers
        audiobook_files = self._find_audiobook_files(directory, recursive)
        self.sync_stats['total_files'] = len(audiobook_files)
        
        logger.info(f"📁 {len(audiobook_files)} fichiers trouvés")
        
        # Authentification
        if not self.client.authenticate():
            return {'success': False, 'error': 'Authentication failed'}
            
        # Synchronisation des fichiers
        for i, file_path in enumerate(audiobook_files):
            try:
                self._sync_single_file(file_path, library_id)
                self.sync_stats['uploaded_files'] += 1
                
                # Callback de progression
                progress = int((i + 1) / len(audiobook_files) * 100)
                self.client.sync_progress_callback(progress, f"Upload de {file_path.name}")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la synchronisation de {file_path}: {e}")
                self.sync_stats['failed_files'] += 1
                
        self.sync_stats['end_time'] = time.time()
        
        # Statistiques finales
        duration = self.sync_stats['end_time'] - self.sync_stats['start_time']
        stats = {
            'success': True,
            'stats': self.sync_stats,
            'duration': duration,
            'files_per_second': self.sync_stats['uploaded_files'] / duration if duration > 0 else 0
        }
        
        logger.info(f"✅ Synchronisation terminée en {duration:.2f}s")
        return stats
        
    def _find_audiobook_files(self, directory: Path, recursive: bool = True) -> List[Path]:
        """Trouver les fichiers audiobooks dans un répertoire"""
        extensions = ['.m4b', '.mp3', '.m4a', '.aac', '.flac']
        pattern = "**/*" if recursive else "*"
        
        files = []
        for ext in extensions:
            files.extend(directory.glob(f"{pattern}{ext}"))
            
        return sorted(files)
        
    def _sync_single_file(self, file_path: Path, library_id: Optional[str]):
        """Synchroniser un fichier unique"""
        logger.info(f"📤 Synchronisation: {file_path.name}")
        
        # Extraction des métadonnées
        metadata = self._extract_metadata(file_path)
        
        # Vérification si le fichier existe déjà
        existing_items = self.client.search_items(metadata.get('title', file_path.stem))
        if existing_items:
            logger.info(f"⏭️ Fichier déjà existant: {file_path.name}")
            self.sync_stats['skipped_files'] += 1
            return
            
        # Upload
        result = self.client.upload_audiobook(file_path, metadata, library_id)
        if not result:
            raise Exception(f"Upload failed for {file_path}")
            
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extraire les métadonnées d'un fichier audio"""
        try:
            from mutagen.mp4 import MP4
            from mutagen.mp3 import MP3
            
            metadata = {
                'title': file_path.stem,
                'author': '',
                'series': '',
                'description': '',
                'duration': 0,
                'size': file_path.stat().st_size,
                'format': file_path.suffix.lower()
            }
            
            # Extraction selon le format
            if file_path.suffix.lower() in ['.m4b', '.m4a']:
                audio_file = MP4(file_path)
                if audio_file.tags:
                    metadata['title'] = str(audio_file.tags.get('\xa9nam', file_path.stem))
                    metadata['author'] = str(audio_file.tags.get('\xa9ART', ''))
                    metadata['description'] = str(audio_file.tags.get('\xa9cmt', ''))
                    metadata['duration'] = int(audio_file.info.length) if audio_file.info else 0
                    
            elif file_path.suffix.lower() == '.mp3':
                audio_file = MP3(file_path)
                if audio_file.tags:
                    metadata['title'] = str(audio_file.tags.get('TIT2', file_path.stem))
                    metadata['author'] = str(audio_file.tags.get('TPE1', ''))
                    metadata['description'] = str(audio_file.tags.get('COMM::eng', ''))
                    metadata['duration'] = int(audio_file.info.length) if audio_file.info else 0
                    
            return metadata
            
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'extraire les métadonnées de {file_path}: {e}")
            return {
                'title': file_path.stem,
                'author': '',
                'series': '',
                'description': '',
                'duration': 0,
                'size': file_path.stat().st_size,
                'format': file_path.suffix.lower()
            }

def create_audiobookshelf_client(config: AudiobookshelfConfig) -> AudiobookshelfClient:
    """Créer un client Audiobookshelf configuré"""
    return AudiobookshelfClient(config)

def create_sync_manager(client: AudiobookshelfClient) -> AudiobookshelfSyncManager:
    """Créer un gestionnaire de synchronisation"""
    return AudiobookshelfSyncManager(client)