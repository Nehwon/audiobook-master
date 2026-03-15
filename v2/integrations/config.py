"""
🔧 Configuration Audiobookshelf - Audiobook Manager Pro
Configuration pour l'intégration avec Audiobookshelf
"""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path

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
    
    @classmethod
    def from_env(cls) -> 'AudiobookshelfConfig':
        """Créer la configuration depuis les variables d'environnement"""
        return cls(
            host=os.getenv('AUDIOBOOKSHELF_HOST', 'localhost'),
            port=int(os.getenv('AUDIOBOOKSHELF_PORT', '13378')),
            username=os.getenv('AUDIOBOOKSHELF_USERNAME', ''),
            password=os.getenv('AUDIOBOOKSHELF_PASSWORD', ''),
            use_ssl=os.getenv('AUDIOBOOKSHELF_USE_SSL', 'false').lower() == 'true',
            timeout=int(os.getenv('AUDIOBOOKSHELF_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('AUDIOBOOKSHELF_RETRY_ATTEMPTS', '3')),
            retry_delay=float(os.getenv('AUDIOBOOKSHELF_RETRY_DELAY', '1.0'))
        )
        
    @classmethod
    def from_file(cls, config_file: Path) -> 'AudiobookshelfConfig':
        """Créer la configuration depuis un fichier"""
        import json
        
        if not config_file.exists():
            return cls()
            
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                return cls(**data)
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de la configuration: {e}")
            return cls()
            
    def to_file(self, config_file: Path):
        """Sauvegarder la configuration dans un fichier"""
        import json
        
        config_data = {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'use_ssl': self.use_ssl,
            'timeout': self.timeout,
            'retry_attempts': self.retry_attempts,
            'retry_delay': self.retry_delay
        }
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
            
    def validate(self) -> list[str]:
        """Valider la configuration et retourner les erreurs"""
        errors = []
        
        if not self.host:
            errors.append("L'hôte est requis")
            
        if not (1 <= self.port <= 65535):
            errors.append("Le port doit être entre 1 et 65535")
            
        if not self.username:
            errors.append("Le nom d'utilisateur est requis")
            
        if not self.password:
            errors.append("Le mot de passe est requis")
            
        if self.timeout <= 0:
            errors.append("Le timeout doit être positif")
            
        if self.retry_attempts <= 0:
            errors.append("Le nombre de tentatives doit être positif")
            
        return errors
        
    def get_base_url(self) -> str:
        """Obtenir l'URL de base de l'API"""
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"

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
    
    @classmethod
    def from_env(cls) -> 'SyncConfig':
        """Créer la configuration depuis les variables d'environnement"""
        return cls(
            enabled=os.getenv('SYNC_ENABLED', 'false').lower() == 'true',
            auto_sync=os.getenv('SYNC_AUTO', 'false').lower() == 'true',
            library_id=os.getenv('SYNC_LIBRARY_ID') or None,
            upload_after_conversion=os.getenv('SYNC_UPLOAD_AFTER_CONVERSION', 'true').lower() == 'true',
            conflict_resolution=os.getenv('SYNC_CONFLICT_RESOLUTION', 'skip'),
            batch_size=int(os.getenv('SYNC_BATCH_SIZE', '10')),
            retry_failed_uploads=os.getenv('SYNC_RETRY_FAILED', 'true').lower() == 'true',
            max_retry_attempts=int(os.getenv('SYNC_MAX_RETRY_ATTEMPTS', '3'))
        )
        
    @classmethod
    def from_file(cls, config_file: Path) -> 'SyncConfig':
        """Créer la configuration depuis un fichier"""
        import json
        
        if not config_file.exists():
            return cls()
            
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                return cls(**data)
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de la configuration: {e}")
            return cls()
            
    def to_file(self, config_file: Path):
        """Sauvegarder la configuration dans un fichier"""
        import json
        
        config_data = {
            'enabled': self.enabled,
            'auto_sync': self.auto_sync,
            'library_id': self.library_id,
            'upload_after_conversion': self.upload_after_conversion,
            'conflict_resolution': self.conflict_resolution,
            'batch_size': self.batch_size,
            'retry_failed_uploads': self.retry_failed_uploads,
            'max_retry_attempts': self.max_retry_attempts
        }
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
            
    def validate(self) -> list[str]:
        """Valider la configuration et retourner les erreurs"""
        errors = []
        
        if self.conflict_resolution not in ['skip', 'overwrite', 'merge']:
            errors.append("Le mode de résolution de conflit doit être 'skip', 'overwrite' ou 'merge'")
            
        if self.batch_size <= 0:
            errors.append("La taille du batch doit être positive")
            
        if self.max_retry_attempts <= 0:
            errors.append("Le nombre maximum de tentatives doit être positif")
            
        return errors

def load_config() -> tuple[AudiobookshelfConfig, SyncConfig]:
    """Charger la configuration depuis les sources par défaut"""
    config_dir = Path.home() / '.audiobook-manager'
    
    # Configuration Audiobookshelf
    abs_config_file = config_dir / 'audiobookshelf.json'
    abs_config = AudiobookshelfConfig.from_file(abs_config_file)
    
    # Configuration de synchronisation
    sync_config_file = config_dir / 'sync.json'
    sync_config = SyncConfig.from_file(sync_config_file)
    
    return abs_config, sync_config

def save_config(abs_config: AudiobookshelfConfig, sync_config: SyncConfig):
    """Sauvegarder la configuration"""
    config_dir = Path.home() / '.audiobook-manager'
    config_dir.mkdir(exist_ok=True)
    
    # Sauvegarde Audiobookshelf
    abs_config_file = config_dir / 'audiobookshelf.json'
    abs_config.to_file(abs_config_file)
    
    # Sauvegarde synchronisation
    sync_config_file = config_dir / 'sync.json'
    sync_config.to_file(sync_config_file)