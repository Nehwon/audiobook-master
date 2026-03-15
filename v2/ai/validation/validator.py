#!/usr/bin/env python3
"""
Validateur de qualité IA - Audiobook Manager Pro
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationConfig:
    """Configuration du validateur de qualité"""
    min_synopsis_length: int = 50
    max_synopsis_length: int = 300
    max_genres: int = 3
    max_tags: int = 10
    max_description_length: int = 500
    min_cover_resolution: tuple = (600, 600)
    max_cover_size: int = 2097152  # 2MB
    forbidden_words: List[str] = None
    
    def __post_init__(self):
        if self.forbidden_words is None:
            self.forbidden_words = ["spoiler", "meurt", "fin", "révélation", "mort", "tue", "tuer", "assassinat"]

class QualityValidator:
    """Validateur de qualité pour les métadonnées IA générées"""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les métadonnées complètes"""
        try:
            logger.info("🔍 Validation métadonnées IA")
            
            validation_result = {
                'valid': True,
                'score': 0,
                'issues': [],
                'warnings': [],
                'details': {}
            }
            
            # Validation des champs requis
            required_fields = ['title', 'author', 'description']
            for field in required_fields:
                if not metadata.get(field):
                    validation_result['valid'] = False
                    validation_result['issues'].append(f"Champ requis manquant: {field}")
            
            # Validation synopsis
            if 'synopsis' in metadata:
                synopsis_result = self._validate_synopsis(metadata['synopsis'])
                validation_result['details']['synopsis'] = synopsis_result
                if not synopsis_result['valid']:
                    validation_result['valid'] = False
                    validation_result['issues'].extend(synopsis_result['issues'])
            
            # Validation genres
            if 'genres' in metadata:
                genres_result = self._validate_genres(metadata['genres'])
                validation_result['details']['genres'] = genres_result
                if not genres_result['valid']:
                    validation_result['valid'] = False
                    validation_result['issues'].extend(genres_result['issues'])
            
            # Validation tags
            if 'tags' in metadata:
                tags_result = self._validate_tags(metadata['tags'])
                validation_result['details']['tags'] = tags_result
                if not tags_result['valid']:
                    validation_result['valid'] = False
                    validation_result['issues'].extend(tags_result['issues'])
            
            # Validation description
            if 'description' in metadata:
                desc_result = self._validate_description(metadata['description'])
                validation_result['details']['description'] = desc_result
                if not desc_result['valid']:
                    validation_result['valid'] = False
                    validation_result['issues'].extend(desc_result['issues'])
            
            # Calcul du score de qualité
            validation_result['score'] = self._calculate_quality_score(metadata, validation_result)
            
            # Logs de validation
            if validation_result['valid']:
                logger.info(f"✅ Métadonnées validées (score: {validation_result['score']}/100)")
            else:
                logger.warning(f"⚠️ Métadonnées avec {len(validation_result['issues'])} problèmes (score: {validation_result['score']}/100)")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"💥 Erreur validation métadonnées: {e}")
            return {
                'valid': False,
                'score': 0,
                'issues': [f"Erreur validation: {e}"],
                'warnings': [],
                'details': {}
            }
    
    def _validate_synopsis(self, synopsis: str) -> Dict[str, Any]:
        """Valide le synopsis"""
        result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'score': 0
        }
        
        if not synopsis:
            result['valid'] = False
            result['issues'].append("Synopsis vide")
            return result
        
        # Longueur
        word_count = len(synopsis.split())
        if word_count < self.config.min_synopsis_length:
            result['valid'] = False
            result['issues'].append(f"Synopsis trop court ({word_count} mots, minimum {self.config.min_synopsis_length})")
        elif word_count > self.config.max_synopsis_length:
            result['valid'] = False
            result['issues'].append(f"Synopsis trop long ({word_count} mots, maximum {self.config.max_synopsis_length})")
        
        # Contenu interdit
        synopsis_lower = synopsis.lower()
        for word in self.config.forbidden_words:
            if word in synopsis_lower:
                result['valid'] = False
                result['issues'].append(f"Mot interdit trouvé: {word}")
        
        # Structure
        paragraphs = [p.strip() for p in synopsis.split('\n\n') if p.strip()]
        if len(paragraphs) > 3:
            result['warnings'].append(f"Trop de paragraphes ({len(paragraphs)}, maximum 3)")
        
        # Score
        if result['valid']:
            result['score'] = min(100, 30 + (word_count / self.config.max_synopsis_length) * 70)
        else:
            result['score'] = 0
        
        return result
    
    def _validate_genres(self, genres: List[str]) -> Dict[str, Any]:
        """Valide les genres"""
        result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'score': 0
        }
        
        if not genres:
            result['valid'] = False
            result['issues'].append("Aucun genre spécifié")
            return result
        
        # Nombre de genres
        if len(genres) > self.config.max_genres:
            result['valid'] = False
            result['issues'].append(f"Trop de genres ({len(genres)}, maximum {self.config.max_genres})")
        
        # Doublons
        unique_genres = list(set(genres))
        if len(unique_genres) < len(genres):
            result['warnings'].append("Genres en double détectés")
        
        # Score
        if result['valid']:
            result['score'] = min(100, 20 + (len(genres) / self.config.max_genres) * 80)
        else:
            result['score'] = 0
        
        return result
    
    def _validate_tags(self, tags: List[str]) -> Dict[str, Any]:
        """Valide les tags"""
        result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'score': 0
        }
        
        if not tags:
            result['warnings'].append("Aucun tag spécifié")
            return result
        
        # Nombre de tags
        if len(tags) > self.config.max_tags:
            result['valid'] = False
            result['issues'].append(f"Trop de tags ({len(tags)}, maximum {self.config.max_tags})")
        
        # Doublons
        unique_tags = list(set(tags))
        if len(unique_tags) < len(tags):
            result['warnings'].append("Tags en double détectés")
        
        # Longueur des tags
        for tag in tags:
            if len(tag) < 2:
                result['warnings'].append(f"Tag trop court: {tag}")
        
        # Score
        if result['valid']:
            result['score'] = min(100, 15 + (len(tags) / self.config.max_tags) * 85)
        else:
            result['score'] = 0
        
        return result
    
    def _validate_description(self, description: str) -> Dict[str, Any]:
        """Valide la description"""
        result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'score': 0
        }
        
        if not description:
            result['valid'] = False
            result['issues'].append("Description vide")
            return result
        
        # Longueur
        if len(description) > self.config.max_description_length:
            result['valid'] = False
            result['issues'].append(f"Description trop longue ({len(description)} caractères, maximum {self.config.max_description_length})")
        
        # Score
        if result['valid']:
            result['score'] = min(100, 25 + (len(description) / self.config.max_description_length) * 75)
        else:
            result['score'] = 0
        
        return result
    
    def _calculate_quality_score(self, metadata: Dict[str, Any], validation_result: Dict[str, Any]) -> int:
        """Calcule le score de qualité global"""
        try:
            score = 0
            
            # Points de base pour champs requis
            required_fields = ['title', 'author', 'description']
            required_score = sum(1 for field in required_fields if metadata.get(field)) * 20
            score += required_score
            
            # Points pour le synopsis
            if 'synopsis' in validation_result['details']:
                synopsis_score = validation_result['details']['synopsis']['score']
                score += (synopsis_score * 0.3)
            
            # Points pour les genres
            if 'genres' in validation_result['details']:
                genres_score = validation_result['details']['genres']['score']
                score += (genres_score * 0.2)
            
            # Points pour les tags
            if 'tags' in validation_result['details']:
                tags_score = validation_result['details']['tags']['score']
                score += (tags_score * 0.15)
            
            # Points pour la description
            if 'description' in validation_result['details']:
                desc_score = validation_result['details']['description']['score']
                score += (desc_score * 0.25)
            
            return int(min(100, score))
            
        except Exception as e:
            logger.error(f"💥 Erreur calcul score qualité: {e}")
            return 0
    
    def validate_cover(self, cover_path: str) -> Dict[str, Any]:
        """Valide la pochette"""
        try:
            from PIL import Image
            
            result = {
                'valid': True,
                'issues': [],
                'warnings': [],
                'score': 0
            }
            
            with Image.open(cover_path) as img:
                width, height = img.size
                
                # Résolution
                if width < self.config.min_cover_resolution[0] or height < self.config.min_cover_resolution[1]:
                    result['valid'] = False
                    result['issues'].append(f"Résolution trop petite ({width}x{height}, minimum {self.config.min_cover_resolution[0]}x{self.config.min_cover_resolution[1]})")
                
                # Format
                if img.format not in ['JPEG', 'PNG']:
                    result['valid'] = False
                    result['issues'].append(f"Format non supporté: {img.format}")
                
                # Taille fichier
                import os
                file_size = os.path.getsize(cover_path)
                if file_size > self.config.max_cover_size:
                    result['valid'] = False
                    result['issues'].append(f"Fichier trop lourd ({file_size} bytes, maximum {self.config.max_cover_size})")
                
                # Score
                if result['valid']:
                    result['score'] = 100
                else:
                    result['score'] = 0
            
            return result
            
        except Exception as e:
            logger.error(f"💥 Erreur validation pochette: {e}")
            return {
                'valid': False,
                'issues': [f"Erreur validation: {e}"],
                'warnings': [],
                'score': 0
            }

def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Fonction utilitaire pour valider les métadonnées"""
    validator = QualityValidator()
    return validator.validate_metadata(metadata)

if __name__ == "__main__":
    # Test
    test_metadata = {
        'title': 'Test',
        'author': 'Test Author',
        'description': 'Test description',
        'synopsis': 'This is a test synopsis with enough words to pass validation.',
        'genres': ['Roman', 'Fantasy'],
        'tags': ['test', 'example']
    }
    
    result = validate_metadata(test_metadata)
    print(f"Validation result: {result}")