#!/usr/bin/env python3
"""
Classificateur de genres avec IA - Audiobook Manager Pro
"""

import subprocess
import json
import logging
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ClassificationConfig:
    """Configuration du classificateur de genres"""
    model: str = "llama2:7b"
    max_tokens: int = 100
    temperature: float = 0.3  # Plus bas pour cohérence
    top_p: float = 0.9
    
    # Mapping des genres
    genres_mapping: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.genres_mapping is None:
            self.genres_mapping = {
                'fiction': ["Roman", "Science-fiction", "Fantasy", "Policier", "Thriller", "Drame", "Comédie", "Aventure", "Historique", "Romance"],
                'non_fiction': ["Biographie", "Histoire", "Essai", "Documentaire", "Science", "Technique", "Philosophie", "Psychologie", "Sociologie", "Politique"],
                'young_adult': ["Jeunesse", "Adolescent", "Fantasy YA", "Romance YA", "Aventure YA", "Scolaire", "Famille"],
                'children': ["Enfants", "Contes", "Éducatif", "Aventure enfant", "Comptines", "Apprentissage"]
            }

class GenreClassifier:
    """Classificateur de genres avec IA"""
    
    def __init__(self, config: Optional[ClassificationConfig] = None):
        self.config = config or ClassificationConfig()
    
    def classify_genres(self, title: str, author: str, existing_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Classifie les genres avec IA et validation"""
        try:
            logger.info(f"🏷️ Classification genres IA: {author} - {title}")
            
            # Construction du prompt
            prompt = self._build_prompt(title, author, existing_description)
            
            # Appel Ollama
            classification = self._call_ollama(prompt)
            
            if not classification:
                logger.warning("❌ Classification vide reçue d'Ollama")
                return None
            
            # Validation de la classification
            validated_classification = self._validate_classification(classification, title, author)
            
            if validated_classification:
                logger.info(f"✅ Classification validée: {validated_classification.get('primary_genre', 'inconnu')}")
                return validated_classification
            else:
                logger.warning("❌ Classification non validée")
                return None
                
        except Exception as e:
            logger.error(f"💥 Erreur classification genres: {e}")
            return None
    
    def _build_prompt(self, title: str, author: str, existing_description: Optional[str]) -> str:
        """Construit le prompt pour Ollama"""
        genres_list = []
        for category, genres in self.config.genres_mapping.items():
            genres_list.extend(genres)
        
        base_prompt = f"""Analyse "{title}" de {author} et classifie dans les catégories suivantes:
{', '.join(genres_list)}

Informations disponibles:
- Titre: {title}
- Auteur: {author}"""
        
        if existing_description:
            base_prompt += f"\n- Description: {existing_description}"
        
        base_prompt += f"""

Instructions:
1. Analyse le titre, l'auteur et la description pour déterminer le genre
2. Retourne le genre principal le plus probable
3. Propose 2 genres secondaires pertinents
4. Donne un score de confiance (0.0 à 1.0)
5. Explique brièvement le raisonnement (1-2 phrases)
6. Format JSON strict avec ces champs uniquement:
{{"primary_genre": "genre_principal", "secondary_genres": ["genre1", "genre2"], "confidence": 0.85, "reasoning": "explication_breve"}}

Exemples de genres: {', '.join(genres_list[:10])}...

Retourne uniquement le JSON, pas d'explications supplémentaires."""
        
        return base_prompt
    
    def _call_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Appelle Ollama pour classifier les genres"""
        try:
            cmd = [
                'ollama', 'run', 
                self.config.model,
                prompt
            ]
            
            logger.debug(f"🤖 Appel Ollama: {self.config.model}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=45,
                check=True
            )
            
            response = result.stdout.strip()
            logger.debug(f"🤖 Réponse brute Ollama: {response[:100]}...")
            
            # Extraction du JSON
            classification = self._extract_classification_from_response(response)
            return classification
            
        except subprocess.TimeoutExpired:
            logger.error("⏰ Timeout Ollama (>45s)")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erreur Ollama: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"💥 Erreur appel Ollama: {e}")
            return None
    
    def _extract_classification_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrait la classification de la réponse Ollama"""
        try:
            # Essai 1: Extraction JSON
            json_match = re.search(r'\{.*?"primary_genre".*?\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data
            
            # Essai 2: Extraction avec regex plus souple
            pattern = r'"primary_genre"\s*:\s*"([^"]+)"\s*,\s*"secondary_genres"\s*:\s*\[([^\]]+)\]\s*,\s*"confidence"\s*:\s*([0-9.]+)\s*,\s*"reasoning"\s*:\s*"([^"]*)"'
            match = re.search(pattern, response)
            if match:
                primary_genre = match.group(1)
                secondary_genres_str = match.group(2)
                confidence = float(match.group(3))
                reasoning = match.group(4)
                
                # Parse secondary genres
                secondary_genres = [g.strip().strip('"') for g in secondary_genres_str.split(',')]
                
                return {
                    'primary_genre': primary_genre,
                    'secondary_genres': secondary_genres,
                    'confidence': confidence,
                    'reasoning': reasoning
                }
            
            logger.warning("⚠️ Classification non trouvée dans la réponse Ollama")
            return None
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Réponse Ollama non JSON valide")
            return None
        except Exception as e:
            logger.error(f"💥 Erreur extraction classification: {e}")
            return None
    
    def _validate_classification(self, classification: Dict[str, Any], title: str, author: str) -> Optional[Dict[str, Any]]:
        """Valide la classification selon les règles qualité"""
        try:
            # Validation structure
            required_fields = ['primary_genre', 'secondary_genres', 'confidence', 'reasoning']
            for field in required_fields:
                if field not in classification:
                    logger.warning(f"⚠️ Champ manquant: {field}")
                    return None
            
            # Validation primary genre
            primary_genre = classification['primary_genre']
            if not primary_genre or len(primary_genre) < 2:
                logger.warning("⚠️ Genre principal invalide")
                return None
            
            # Validation secondary genres
            secondary_genres = classification['secondary_genres']
            if not isinstance(secondary_genres, list) or len(secondary_genres) < 1:
                logger.warning("⚠️ Genres secondaires invalides")
                return None
            
            # Validation confidence
            confidence = classification['confidence']
            if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                logger.warning("⚠️ Confiance invalide")
                return None
            
            # Validation reasoning
            reasoning = classification['reasoning']
            if not reasoning or len(reasoning) < 10:
                logger.warning("⚠️ Raisonnement trop court")
                return None
            
            # Validation cohérence
            if not self._validate_consistency(classification, title, author):
                logger.warning("⚠️ Classification incohérente")
                return None
            
            logger.info(f"✅ Classification validée: {primary_genre} (confiance: {confidence})")
            return classification
            
        except Exception as e:
            logger.error(f"💥 Erreur validation classification: {e}")
            return None
    
    def _validate_consistency(self, classification: Dict[str, Any], title: str, author: str) -> bool:
        """Valide la cohérence de la classification"""
        primary_genre = classification['primary_genre'].lower()
        secondary_genres = [g.lower() for g in classification['secondary_genres']]
        confidence = classification['confidence']
        
        # Vérification redondance
        if primary_genre in secondary_genres:
            logger.warning("⚠️ Redondance genre principal/secondaire")
            return False
        
        # Vérification confiance minimale
        if confidence < 0.5:
            logger.warning(f"⚠️ Confiance trop faible: {confidence}")
            return False
        
        # Vérification nombre genres secondaires
        if len(secondary_genres) > 3:
            logger.warning("⚠️ Trop de genres secondaires")
            return False
        
        # Vérification pertinence basique (check si les genres existent dans notre mapping)
        all_genres = [primary_genre] + secondary_genres
        valid_genres = []
        for category, genres in self.config.genres_mapping.items():
            valid_genres.extend([g.lower() for g in genres])
        
        for genre in all_genres:
            if genre not in valid_genres:
                logger.warning(f"⚠️ Genre inconnu: {genre}")
                return False
        
        return True

def classify_genres(title: str, author: str, existing_description: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fonction utilitaire pour classifier les genres"""
    classifier = GenreClassifier()
    return classifier.classify_genres(title, author, existing_description)

if __name__ == "__main__":
    # Test
    classification = classify_genres("Les Misérables", "Victor Hugo")
    if classification:
        print(f"Classification générée:\n{classification}")
    else:
        print("❌ Échec classification genres")