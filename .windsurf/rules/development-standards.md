# Règles de Développement pour Audiobook Manager Pro

## 🎯 Principes Directeurs

### 🚀 Performance First
- Optimisation GPU prioritaire
- Monitoring temps réel obligatoire
- Benchmarks pour nouvelles features
- Scalabilité dès la conception

### 🎨 UX Centric
- Interface intuitive et responsive
- Feedback utilisateur immédiat
- Accessibilité WCAG 2.1 AA
- Mobile-first design

### 🔒 Sécurité par Défaut
- Validation entrées systématique
- Pas de secrets en code
- Moins de privilèges possible
- Audit sécurité régulier

### 🧪 Test Driven
- Tests avant production
- Couverture >80% obligatoire
- Tests E2E pour workflows critiques
- Performance tests automatisés

## 📁 Structure de Code

### 🐍 Python Architecture
```
audiobook_manager/
├── core/                 # Logique métier principale
│   ├── processor.py       # Conversion audio
│   ├── metadata.py        # Gestion métadonnées
│   └── gpu.py           # Accélération GPU
├── web/                  # Interface web
│   ├── api/              # Endpoints REST
│   ├── static/           # Assets frontend
│   └── templates/        # Templates HTML
├── integrations/          # Services tiers
│   ├── plex.py          # Integration Plex
│   ├── jellyfin.py       # Integration Jellyfin
│   └── cloud.py          # Stockage cloud
├── ai/                   # Intelligence artificielle
│   ├── synopsis.py       # Génération synopsis
│   ├── classification.py  # Classification genres
│   └── validation.py     # Qualité IA
├── tests/                 # Tests automatisés
├── docs/                  # Documentation
└── config/                # Configuration
```

### 🌐 Frontend Structure
```
static/
├── css/                  # Styles Tailwind
├── js/                   # JavaScript vanilla
├── images/               # Images et icônes
└── components/            # Composants réutilisables
```

## 🎯 Règles de Codage

### 🐍 Python Standards
```python
# Imports ordonnés avec isort
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict

from flask import Flask, request, jsonify
import mutagen
import requests

# Type hints obligatoires
def process_audio(
    input_path: Path,
    output_path: Path,
    options: Dict[str, str]
) -> bool:
    """
    Traite un fichier audio avec les options spécifiées.
    
    Args:
        input_path: Chemin du fichier d'entrée
        output_path: Chemin du fichier de sortie
        options: Options de conversion
        
    Returns:
        True si succès, False sinon
    """
    try:
        # Logique de traitement
        return True
    except Exception as e:
        logger.error(f"Erreur traitement: {e}")
        return False

# Constants en majuscules
DEFAULT_BITRATE = "128k"
SUPPORTED_FORMATS = [".mp3", ".m4a", ".wav", ".flac"]
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
```

### 🌐 JavaScript Standards
```javascript
// ES6+ avec JSDoc
/**
 * Initialise la connexion WebSocket
 * @param {string} url - URL du serveur WebSocket
 * @param {Function} onMessage - Callback pour messages
 */
function initWebSocket(url, onMessage) {
    const socket = new WebSocket(url);
    
    socket.onopen = () => {
        console.log('WebSocket connecté');
        updateStatus('connected');
    };
    
    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage(data);
        } catch (error) {
            console.error('Erreur parsing message:', error);
        }
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket erreur:', error);
        updateStatus('error');
    };
    
    return socket;
}

// Constants en majuscules
const API_BASE_URL = '/api';
const UPDATE_INTERVAL = 1000;
const MAX_RETRIES = 5;
```

## 🔄 Workflow de Développement

### 1. Création Feature
```bash
# Depuis dev
git checkout dev
git pull origin dev

# Nouvelle branche feature
git checkout -b feature/nom-feature

# Développement avec tests
# ... code ...
# ... tests ...

# Commit avec format conventionnel
git add .
git commit -m "feat(processor): ajout conversion GPU RTX 4070"
```

### 2. Review Process
- **Code Review**: 2 reviewers minimum
- **Tests**: Coverage >80% obligatoire
- **Performance**: Benchmarks verts
- **Sécurité**: Validation entrées
- **Documentation**: API et README mis à jour

### 3. Integration
```bash
# Merge dans dev
git checkout dev
git merge --no-ff feature/nom-feature

# Tests d'intégration
pytest tests/integration/

# Push vers dev
git push origin dev
```

### 4. Release Process
```bash
# Branche release
git checkout dev
git checkout -b release/v2.1.0

# Update version et CHANGELOG
# ... mise à jour ...

# Tests finaux
pytest tests/ --cov

# Merge dans main
git checkout main
git merge --no-ff release/v2.1.0
git tag v2.1.0

# Push
git push origin main --tags
```

## 🧪 Standards de Tests

### 📊 Types de Tests
```python
# Tests unitaires
def test_parse_filename():
    """Test parsing nom de fichier"""
    processor = AudiobookProcessor()
    metadata = processor.parse_filename("Auteur - Titre.zip")
    assert metadata.author == "Auteur"
    assert metadata.title == "Titre"

# Tests d'intégration
def test_full_conversion_workflow():
    """Test workflow complet conversion"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup fichiers test
        input_file = create_test_audio_file(tmpdir)
        output_file = Path(tmpdir) / "output.m4b"
        
        # Execution
        processor = AudiobookProcessor()
        success = processor.convert_to_m4b(input_file, output_file)
        
        # Validation
        assert success
        assert output_file.exists()
        assert validate_m4b_file(output_file)

# Tests performance
def test_conversion_performance():
    """Test performance conversion GPU"""
    start_time = time.time()
    
    processor = AudiobookProcessor()
    processor.convert_to_m4b(test_file, output_file)
    
    duration = time.time() - start_time
    assert duration < 300  # <5 minutes pour fichier test
```

## 📊 Métriques et Monitoring

### 📈 KPIs Développement
- **Velocity**: Points/story par sprint
- **Quality**: % bugs post-production
- **Coverage**: % code couvert par tests
- **Performance**: Temps conversion moyen

### 🚨 Alertes Qualité
- **Coverage** <80%: Bloque merge
- **Performance** -20%: Investigation requise
- **Security**: Vulnérabilité critique: Hotfix immédiat
- **UX**: Temps réponse >3s: Optimisation requise

## 🎯 Bonnes Pratiques

### ✅ À Faire
- Commits petits et fréquents
- Tests avant chaque commit
- Documentation mise à jour
- Code review systématique
- Performance monitoring

### ❌ À Éviter
- Secrets en dur dans code
- Commits massifs monolithiques
- Code sans tests
- Documentation obsolète
- Ignorer alertes performance

### 🔧 Outils Obligatoires
- **Formatage**: black, isort
- **Linting**: flake8, mypy
- **Tests**: pytest, coverage
- **Sécurité**: bandit
- **Performance**: pytest-benchmark

---
*Règles maintenues activement*  
*Version: 2.0.0*  
*Dernière mise à jour: 2026-03-01*
