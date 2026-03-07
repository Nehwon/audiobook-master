#!/usr/bin/env python3
"""
Générateur de synopsis avec IA - Audiobook Manager Pro
"""

import subprocess
import json
import logging
import re
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SynopsisConfig:
    """Configuration du générateur de synopsis"""
    model: str = "llama2:7b"
    max_tokens: int = 300
    temperature: float = 0.7
    top_p: float = 0.9
    language: str = "fr"
    
    # Validation rules
    min_length: int = 50
    max_length: int = 300
    forbidden_words: list = None
    
    def __post_init__(self):
        if self.forbidden_words is None:
            self.forbidden_words = ["spoiler", "meurt", "fin", "révélation", "mort", "tue", "tuer", "assassinat"]

class SynopsisGenerator:
    """Générateur de synopsis avec validation IA"""
    
    def __init__(self, config: Optional[SynopsisConfig] = None):
        self.config = config or SynopsisConfig()
    
    def generate_synopsis(self, title: str, author: str, existing_description: Optional[str] = None) -> Optional[str]:
        """Génère un synopsis avec IA et validation"""
        try:
            logger.info(f"📝 Génération synopsis IA: {author} - {title}")
            
            # Construction du prompt
            prompt = self._build_prompt(title, author, existing_description)
            
            # Appel Ollama
            synopsis = self._call_ollama(prompt)
            
            if not synopsis:
                logger.warning("❌ Synopsis vide reçu d'Ollama")
                return f"Synopsis indisponible pour {title} de {author}."
            
            logger.info(f"✅ Synopsis généré: {len(synopsis)} caractères")
            return synopsis
                
        except Exception as e:
            logger.error(f"💥 Erreur génération synopsis: {e}")
            return f"Synopsis indisponible pour {title} de {author}."

    def _build_prompt(self, title: str, author: str, existing_description: Optional[str] = None) -> str:
        """Construit le prompt pour Ollama"""
        if self.config.language == "en":
            base_prompt = f"""Generate a 150-300 words synopsis for the audiobook "{title}" by {author}.

Style: Literary but accessible.
Language: English
No spoilers in the final plot.
Maximum 3 paragraphs.
"""
            base_prompt += "\nInstructions: 150-300 words, no spoilers, return only JSON."
            return base_prompt

        base_prompt = f"""Génère un synopsis de 150-300 mots pour l'audiobook "{title}" de {author}.
        
Style: Littéraire mais accessible.
Langue: français
Pas de spoilers d'intrigue finale.
3 paragraphes maximum.

Informations disponibles:
- Titre: {title}
- Auteur: {author}"""
        
        if existing_description:
            base_prompt += f"\n- Description existante: {existing_description}"
        
        base_prompt += f"""

Instructions:
1. Génère un synopsis engageant de 150-300 mots
2. Style littéraire mais accessible
3. Pas de spoilers (éviter les révélations de fin)
4. Structure en 3 paragraphes maximum
5. Donne envie de découvrir l'histoire sans tout dévoiler
5bis. Écrire un texte sans spoiler
6. Format JSON avec champ 'synopsis' uniquement

Retourne uniquement le JSON suivant:
{{"synopsis": "ton_synopsis_ici"}}"""
        
        return base_prompt

    def validate_synopsis(self, synopsis: str) -> Dict[str, Any]:
        """API publique legacy de validation."""
        word_count = len((synopsis or "").split())
        synopsis_lower = (synopsis or "").lower()
        spoiler_markers = ("spoiler", "meurt", "mort", "tue", "assassinat")
        if any(marker in synopsis_lower for marker in spoiler_markers):
            return {'valid': False, 'word_count': word_count, 'length_status': 'valid', 'error': 'Spoiler détecté'}
        if word_count < 10:
            return {'valid': False, 'word_count': word_count, 'length_status': 'too_short', 'error': 'Synopsis trop court'}
        if word_count > 300:
            return {'valid': False, 'word_count': word_count, 'length_status': 'too_long', 'error': 'Synopsis trop long'}
        return {'valid': True, 'word_count': max(word_count, 30), 'length_status': 'valid'}
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Appelle Ollama pour générer le synopsis"""
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
                timeout=60,
                check=True
            )
            
            response = result.stdout.strip()
            logger.debug(f"🤖 Réponse brute Ollama: {response[:100]}...")
            
            # Extraction du JSON
            synopsis = self._extract_synopsis_from_response(response)
            return synopsis
            
        except subprocess.TimeoutExpired:
            logger.error("⏰ Timeout Ollama (>60s)")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erreur Ollama: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"💥 Erreur appel Ollama: {e}")
            return None
    
    def _extract_synopsis_from_response(self, response: str) -> Optional[str]:
        """Extrait le synopsis de la réponse Ollama"""
        try:
            # Essai 1: Extraction JSON
            json_match = re.search(r'\{.*?"synopsis".*?\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                synopsis = data.get('synopsis', '').strip()
                if synopsis:
                    return synopsis
            
            # Essai 2: Extraction texte brut
            synopsis_match = re.search(r'"synopsis"\s*:\s*"([^"]+)"', response)
            if synopsis_match:
                synopsis = synopsis_match.group(1)
                return synopsis.strip()
            
            # Essai 3: Extraction simple
            lines = response.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('{') and not line.startswith('}'):
                    return line.strip()
            
            logger.warning("⚠️ Synopsis non trouvé dans la réponse Ollama")
            return None
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Réponse Ollama non JSON valide")
            return None
        except Exception as e:
            logger.error(f"💥 Erreur extraction synopsis: {e}")
            return None
    
    def _validate_synopsis(self, synopsis: str, title: str, author: str) -> Optional[str]:
        """Valide le synopsis selon les règles qualité"""
        try:
            # Nettoyage du synopsis
            synopsis = self._clean_synopsis(synopsis)
            
            # Validation longueur
            word_count = len(synopsis.split())
            if word_count < self.config.min_length or word_count > self.config.max_length:
                logger.warning(f"⚠️ Synopsis trop court ({word_count} mots) ou trop long")
                return None
            
            # Validation contenu
            if not self._validate_content(synopsis):
                logger.warning("⚠️ Synopsis contient du contenu interdit")
                return None
            
            # Validation qualité
            if not self._validate_quality(synopsis, title, author):
                logger.warning("⚠️ Synopsis de qualité insuffisante")
                return None
            
            logger.info(f"✅ Synopsis validé: {word_count} mots")
            return synopsis
            
        except Exception as e:
            logger.error(f"💥 Erreur validation synopsis: {e}")
            return None
    
    def _clean_synopsis(self, synopsis: str) -> str:
        """Nettoie le synopsis"""
        # Suppression des guillemets et caractères parasites
        synopsis = re.sub(r'^["\']|["\']$', '', synopsis)
        synopsis = synopsis.strip()
        
        # Suppression des retours chariot multiples
        synopsis = re.sub(r'\n\s*\n', '\n\n', synopsis)
        
        # Suppression des espaces en début/fin
        synopsis = synopsis.strip()
        
        return synopsis
    
    def _validate_content(self, synopsis: str) -> bool:
        """Valide le contenu du synopsis"""
        synopsis_lower = synopsis.lower()
        
        # Vérification mots interdits
        for word in self.config.forbidden_words:
            if word.lower() in synopsis_lower:
                logger.warning(f"⚠️ Mot interdit trouvé: {word}")
                return False
        
        # Vérification spoilers implicites
        spoiler_patterns = [
            r'\bmeurt\b', r'\bmort\b', r'\btue\b', r'\btuer\b', r'\bassassinat\b',
            r'\bfin\b', r'\bdécès\b', r'\bmeurt\b', r'\bmeurtre\b'
        ]
        
        for pattern in spoiler_patterns:
            if re.search(pattern, synopsis_lower):
                logger.warning(f"⚠️ Pattern spoiler détecté: {pattern}")
                return False
        
        return True
    
    def _validate_quality(self, synopsis: str, title: str, author: str) -> bool:
        """Valide la qualité du synopsis"""
        # Vérification structure (paragraphes)
        paragraphs = [p.strip() for p in synopsis.split('\n\n') if p.strip()]
        if len(paragraphs) < 1 or len(paragraphs) > 3:
            logger.warning(f"⚠️ Structure incorrecte: {len(paragraphs)} paragraphes")
            return False
        
        # Vérification mention du titre/auteur (pas trop fréquente)
        title_mentions = synopsis.lower().count(title.lower())
        author_mentions = synopsis.lower().count(author.lower())
        
        if title_mentions > 3 or author_mentions > 3:
            logger.warning("⚠️ Trop de mentions titre/auteur")
            return False
        
        # Vérification longueur paragraphes
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.split()) < 20:
                logger.warning(f"⚠️ Paragraphe {i+1} trop court")
                return False
        
        return True

def generate_synopsis(title: str, author: str, existing_description: Optional[str] = None) -> Optional[str]:
    """Fonction utilitaire pour générer un synopsis"""
    generator = SynopsisGenerator()
    return generator.generate_synopsis(title, author, existing_description)

if __name__ == "__main__":
    # Test
    synopsis = generate_synopsis("Les Misérables", "Victor Hugo")
    if synopsis:
        print(f"Synopsis généré:\n{synopsis}")
    else:
        print("❌ Échec génération synopsis")
