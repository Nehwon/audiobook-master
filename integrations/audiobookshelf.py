#!/usr/bin/env python3
"""
Client pour l'upload vers Audiobookshelf
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, List
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AudiobookshelfConfig:
    """Configuration pour Audiobookshelf"""
    host: str
    port: int = 13378
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None

class AudiobookshelfClient:
    def __init__(self, config: AudiobookshelfConfig):
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}"
        self.session = requests.Session()
        self.token = config.token
        
        if not self.token and config.username and config.password:
            self.authenticate()
    
    def authenticate(self) -> bool:
        """Authentification auprès d'Audiobookshelf"""
        try:
            auth_url = f"{self.base_url}/login"
            auth_data = {
                "username": self.config.username,
                "password": self.config.password
            }
            
            response = self.session.post(auth_url, json=auth_data)
            if response.status_code == 200:
                auth_result = response.json()
                self.token = auth_result.get('user', {}).get('token')
                if self.token:
                    self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                    logger.info("Authentification réussie")
                    return True
            
            logger.error("Échec de l'authentification")
            return False
            
        except Exception as e:
            logger.error(f"Erreur authentification: {e}")
            return False
    
    def get_libraries(self) -> List[Dict]:
        """Récupère la liste des bibliothèques"""
        try:
            url = f"{self.base_url}/api/libraries"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json().get('libraries', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Erreur récupération bibliothèques: {e}")
            return []
    
    def upload_audiobook(self, audiobook_path: Path, library_id: str, metadata: Dict) -> bool:
        """Upload un audiobook vers Audiobookshelf"""
        try:
            # Préparation des métadonnées
            upload_data = {
                "title": metadata.get('title', audiobook_path.stem),
                "author": metadata.get('author', 'Inconnu'),
                "series": metadata.get('series'),
                "sequence": metadata.get('series_number'),
                "description": metadata.get('description'),
                "genres": metadata.get('genres', []),
                "year": metadata.get('year'),
                "language": metadata.get('language', 'fr')
            }
            
            # Upload du fichier
            url = f"{self.base_url}/api/libraries/{library_id}/upload"
            
            with open(audiobook_path, 'rb') as f:
                files = {'file': (audiobook_path.name, f, 'audio/m4b')}
                response = self.session.post(url, files=files, data=upload_data)
            
            if response.status_code == 200:
                logger.info(f"✅ Upload réussi: {audiobook_path.name}")
                return True
            else:
                logger.error(f"❌ Échec upload: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur upload {audiobook_path}: {e}")
            return False
    
    def scan_library(self, library_id: str) -> bool:
        """Déclenche un scan de la bibliothèque"""
        try:
            url = f"{self.base_url}/api/libraries/{library_id}/scan"
            response = self.session.post(url)
            
            if response.status_code == 200:
                logger.info("Scan de la bibliothèque déclenché")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur scan bibliothèque: {e}")
            return False
