# 🎧 Audiobook Manager Pro

Système professionnel de traitement et conversion d'audiobooks avec interface web moderne, accélération GPU NVIDIA et métadonnées enrichies.

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
- **Support multi-formats** : MP3, M4A, WAV, FLAC, AAC
- **Archives** : ZIP, RAR

### 🚀 Accélération GPU NVIDIA
- **Détection automatique** RTX 4070/3050
- **Filtres audio accélérés** (normalisation, compression)
- **Surveillance CPU/GPU** en temps réel
- **Optimisation multi-GPU**

### 📊 Monitoring Avancé
- **Barre de progression** précise et fiable
- **Indicateurs d'activité** CPU/GPU
- **Statistiques de performance** en temps réel
- **Analyse des vitesses** de conversion

### 🌐 Scraping Web Intégré
- **Sources multiples** : Google Books API, Babelio
- **Métadonnées complètes** : éditeur, date, description
- **Pochettes HD** automatiques (600x600 JPEG)
- **Validation intelligente** par similarité

### 📚 Métadonnées Riches
- **Parsing intelligent** des noms de fichiers
- **Format série** : Auteur - Série - Tome X - Titre
- **8+ champs FFmpeg** : titre, auteur, éditeur, genre
- **Support Apple Books** compatible

## 🚀 Installation

### Prérequis
```bash
# Python 3.11+
sudo apt update && sudo apt install python3.11 python3.11-pip

# FFmpeg avec support NVIDIA
sudo apt install ffmpeg

# NVIDIA CUDA (pour GPU)
sudo apt install nvidia-cuda-toolkit

# Dépendances Python
pip install mutagen requests beautifulsoup4 pillow
```

### Installation Complète
```bash
# Cloner le dépôt
git clone https://gitea.lamachere.fr/fabrice/audiobooks-master.git
cd audiobooks-master

# Installer les dépendances principales
pip install -r requirements.txt

# Installer les dépendances web
pip install -r requirements_web.txt

# Configurer
cp config.example.py config.py
# Éditer config.py avec vos préférences
```

## 🌐 Lancement de l'Interface Web

### Démarrage
```bash
# Lancer l'interface web
python start_web.py

# Interface disponible sur :
# http://localhost:5000 (local)
# http://192.168.0.120:5000 (réseau)
```

### Accès
- **URL locale** : http://localhost:5000
- **URL réseau** : http://VOTRE_IP:5000
- **WebSocket** : Communication temps réel
- **API REST** : Endpoints pour intégration

## 📖 Utilisation

### Interface Web
1. **Ouvrez** http://localhost:5000
2. **Sélectionnez** un fichier source
3. **Configurez** les options (bitrate, GPU, etc.)
4. **Lancez** la conversion
5. **Suivez** la progression en temps réel
6. **Téléchargez** le fichier M4B

### Ligne de Commande
```bash
# Traiter un seul audiobook
python run.py --source "/path/to/audiobook" --output "/path/to/output"

# Traiter tout un dossier
python run.py --source "/path/to/audiobooks" --output "/path/to/output" --all

# Options avancées
python run.py --source "/path/to/audiobook" --output "/path/to/output" \
  --bitrate 128k --gpu --verbose
```

## ⚙️ Configuration

### `config.py`
```python
# GPU
enable_gpu_acceleration = True

# Audio
audio_bitrate = "192k"
audio_channels = 2
sample_rate = 44100

# Normalisation
enable_loudnorm = True
loudnorm_target = -16
loudnorm_range = 11

# Compression
enable_compressor = True
compressor_settings = "acompressor=threshold=-12dB:ratio=4:attack=5:release=100"

# Scraping
enable_scraping = True

# Dossiers
source_directory = "/home/fabrice/Documents/Audiobooks"
output_directory = "/home/fabrice/Documents/Audiobooks_Processed"
```

## 📁 Structure des Dossiers

```
audiobooks-master/
├── .clinerules/             # Règles CLI et standards
├── .windsurf/               # Configuration Windsurf
├── .git/                    # Dépôt Git
├── ai/                      # Modules IA (synopsis, classification)
│   ├── synopsis/            # Génération de synopsis
│   ├── classification/      # Classification de contenu
│   └── validation/          # Validation métadonnées
├── core/                    # Cœur du projet
│   ├── config.py            # Configuration centralisée
│   ├── main.py              # Point d'entrée principal
│   ├── metadata.py          # Gestion métadonnées
│   └── processor.py         # Logique de traitement
├── integrations/            # Intégrations externes
│   └── audiobookshelf.py    # Client Audiobookshelf
├── web/                     # Interface web
│   └── app.py               # Application Flask
├── src/                     # Sources additionnelles
├── templates/               # Templates HTML
├── static/                  # Ressources statiques (CSS/JS)
├── tests/                   # Tests unitaires
├── logs/                    # Logs applicatifs
├── docs/                    # Documentation
├── Archives/                # Versions précédentes
├── run.py                   # Point d'entrée CLI
├── start_web.py             # Lancement interface web
├── requirements.txt         # Dépendances principales
├── requirements_web.txt     # Dépendances web
├── README.md                # Documentation projet
├── CHANGELOG.md             # Historique versions
├── TODO.md                  # Tâches en cours
├── ROADMAP.md               # Plan de développement
└── LICENSE                  # Licence MIT
```

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
- **core/metadata.py** : 43% coverage (scraping, validation)
- **core/main.py** : 73% coverage (arguments, CLI)
- **Total** : 58% coverage global (record historique !) ✅
- **Tests** : 152/152 tests passants (100%)

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
