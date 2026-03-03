# 🎧 Audiobook Manager Pro

Système professionnel de traitement et conversion d'audiobooks avec interface web moderne, accélération GPU NVIDIA et métadonnées enrichies.

## 🚨 RAPPORT DE BUGS CRITIQUES - Mars 2026

### Bugs Identifiés et Corrigés

#### 🐛 **Bug #1: Double Comptage des Fichiers (CRITIQUE)**
- **Problème**: La fonction `find_audio_files()` comptait les fichiers audio 2 fois
- **Cause**: `glob()` + `rglob()` dans le même dossier
- **Impact**: Taille calculée = 2× taille réelle (1269.4MB au lieu de 634.8MB)
- **Solution**: Suppression de `glob()`, conservation de `rglob()` seul avec déduplication
- **Statut**: ✅ **CORRIGÉ**

#### 🐛 **Bug #2: Fuite Mémoire (CRITIQUE)**
- **Problème**: Processus FFmpeg non terminés correctement
- **Cause**: Pas de nettoyage forcé des processus
- **Impact**: 29GB RAM utilisés anormalement
- **Solution**: Force `terminate()` + `kill()` + `gc.collect()`
- **Statut**: ✅ **CORRIGÉ**

#### 🐛 **Bug #3: Boucle Infinie (MAJEUR)**
- **Problème**: Fichier de sortie dépassait largement la taille d'entrée
- **Cause**: Pas de détection de taille excessive
- **Impact**: Fichiers de +350MB par rapport à la source
- **Solution**: Détection taille maximale (150% de l'entrée)
- **Statut**: ✅ **CORRIGÉ**

#### 🐛 **Bug #4: Surveillance Inefficace (MOYEN)**
- **Problème**: Boucle de progression ne lisait pas correctement FFmpeg
- **Cause**: Mauvaise gestion du stdout/stderr
- **Impact**: Progression bloquée à 0%, ETA incorrect
- **Solution**: Amélioration lecture processus + timeout
- **Statut**: ✅ **CORRIGÉ**

### Approche de Développement Recommandée

#### 🎯 **Phase 1: Concaténation 1:1 Rapide**
- Objectif: Conversion rapide sans réencodage
- Méthode: Simple concaténation des fichiers MP3/M4A existants
- Qualité: Préservée (identique à la source)
- Avantages: Vitesse maximale, taille optimale

#### 🎯 **Phase 2: Réencodage Individuel AAC**
- Objectif: Optimisation taille/qualité
- Méthode: Réencodage fichier par fichier vers AAC 48k
- Qualité: Haute (48kHz, bitrate élevé)
- Avantages: Compression optimale, métadonnées riches

#### 🎯 **Phase 3: Concaténation + Métadonnées**
- Objectif: Fichier M4B final professionnel
- Méthode: Assemblage des fichiers AAC + métadonnées + cover
- Qualité: Optimisée
- Avantages: Format standard, compatibilité maximale

---

## Dernières Mises à Jour (Commit `2f362d1`)

### Nouvelle Structure de Dossiers
- **`.clinerules/`** : Ajout des règles de configuration CLI pour la gestion des workflows et des standards de développement.
- **`ai/`** : Nouveau module d'intelligence artificielle avec :
  - Générateur de synopsis (`ai/synopsis/generator.py`)
  - Classificateur de contenu (`ai/classification/generator.py`)
  - Validateur de métadonnées (`ai/validation/validator.py`)
- **`core/`** : Refonte du cœur du projet avec :
  - `config.py` : Configuration centralisée
  - `main.py` : Point d'entrée principal
  - `metadata.py` : Gestion avancée des métadonnées
  - `processor.py` : Logique de traitement optimisée
- **`integrations/`** : Ajout du client `audiobookshelf.py` pour l'upload automatique vers les bibliothèques Audiobookshelf.
- **`web/`** : Interface web basée sur Flask (`app.py`) pour une gestion visuelle des conversions.

## ✨ Fonctionnalités

### 🌐 Interface Web Moderne
- **Dashboard intuitif** avec design Tailwind CSS
- **Suivi en temps réel** des conversions via WebSocket
- **Gestion visuelle** des fichiers source et convertis
- **Téléchargement direct** depuis l'interface
- **Options de conversion** personnalisables
- **Notifications** en temps réel

### 🎵 Conversion Audio Haute Qualité
- **FFmpeg optimisé** avec FDK-AAC VBR4
- **Bitrates flexibles** : 64k, 96k, 128k, 192k
- **Normalisation EBU R128** optionnelle
- **Compression dynamique** pour voix

### Prérequis
```bash
# Python 3.11+
sudo apt update && sudo apt install python3-pip

# FFmpeg avec support multithreading
sudo apt install ffmpeg

# Dépendances Python
pip install -r requirements.txt
```

### Configuration Rapide
```bash
# Clone du dépôt
git clone https://github.com/fabrice/audiobooks-manager.git
cd audiobooks-manager

# Configuration des dossiers
nano core/config.py  # Modifier source_directory et output_directory

# Lancement rapide
python3 -m core.main --single "Mon Audiobook"
```

## � **Utilisation**

### 🎯 **Modes de Traitement**

#### Phase 1 - Concaténation Rapide
## 🎯 Formats de Noms Supportés

Le système parse automatiquement ces formats :
- `Auteur - Titre`
- `Auteur - Série Tome X - Titre`
- `Auteur - Série Vol X - Titre`
- `Auteur - Titre (Narrateur)`

## 📊 Performance

### GPU NVIDIA RTX 4070
- **Filtres audio** : Accélérés
- **Réduction charge CPU** : 30-50%
- **Temps traitement** : 2x plus rapide
- **Monitoring** : Temps réel

### Qualité Audio
- **Codec** : FDK-AAC VBR4 (meilleur)
- **Bitrates** : 64k-192k flexibles
- **Normalisation** : EBU R128 (-16 LUFS)
- **Compression** : Jusqu'à 80%

## 🌍 API Web

### Endpoints
- `GET /` : Interface web
- `GET /api/status` : Statut des conversions
- `GET /api/files` : Liste fichiers source
- `GET /api/outputs` : Liste fichiers convertis
- `POST /api/convert` : Démarrer conversion
- `POST /api/stop` : Arrêter conversion
- `GET /api/download/<filename>` : Télécharger fichier
- `GET /api/metadata/<filename>` : Métadonnées fichier

### WebSocket Events
- `status_update` : Mise à jour statut
- `conversion_complete` : Conversion terminée
- `conversion_error` : Erreur conversion
- `conversion_stopped` : Conversion arrêtée

## 🔧 Dépannage

### Problèmes Communs
```bash
# Vérifier GPU
nvidia-smi --query-gpu=name --format=csv,noheader

# Vérifier FFmpeg
ffmpeg -hide_banner -encoders | grep aac

# Vérifier dépendances
pip list | grep -E "(mutagen|requests|beautifulsoup4|pillow)"
```

### Logs
```bash
# Activer logs détaillés
python run.py --source "/path/to/audiobook" --output "/path/to/output" --verbose

# Logs dans /tmp/audiobooks/
tail -f /tmp/audiobooks/audiobook_processor.log
```

## 🛠️ Développement

### Tests et Coverage
```bash
# Tests unitaires avec coverage
source venv/bin/activate && PYTHONPATH=. pytest tests/ --cov=core --cov=ai --cov-report=term-missing

# Tests spécifiques
pytest tests/test_config.py -v
pytest tests/test_processor.py -v
pytest tests/test_metadata.py -v

# Coverage complet
pytest --cov=. --cov-report=html --cov-report=term-missing
```

### Tests Unitaires
Le projet inclut une suite complète de tests unitaires :
- **core/config.py** : 100% coverage ✅
- **core/processor.py** : 67% coverage (conversion, parsing, GPU)
- **core/metadata.py** : 73% coverage (scraping, validation)
- **core/main.py** : 73% coverage (arguments, CLI)
- **Total** : 72% coverage global (NOUVEAU RECORD !) ✅
- **Tests** : 181/181 tests passants (100%)

### Contribution
1. Fork le projet
2. Créer une branche `feature/nouvelle-fonctionnalite`
3. Ajouter des tests unitaires pour toute nouvelle fonctionnalité
4. Maintenir le coverage > 90%
5. Commit les changements
6. Push et créer une Pull Request

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus d'informations.

## 📁 Archives

Les fichiers archivés et versions précédentes sont disponibles dans le dossier [Archives](./Archives/README.md).

---

## 🤝 Support

- **Issues** : [Gitea Issues](https://gitea.lamachere.fr/fabrice/audiobooks-master/issues)
- **Documentation** : [Wiki](https://gitea.lamachere.fr/fabrice/audiobooks-master/wiki)

## 🎉 Remerciements

- **FFmpeg** : Pour l'encodage audio
- **Google Books API** : Pour les métadonnées
- **Babelio** : Pour la littérature française
- **NVIDIA** : Pour l'accélération GPU
- **Ollama** : Pour la génération de synopsis

---

**Audiobook Manager Pro** - Transformez vos audiobooks professionnellement ! 🎧✨
