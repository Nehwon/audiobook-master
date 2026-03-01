# 🎧 Audiobook Manager Pro

Système professionnel de traitement et conversion d'audiobooks avec interface web moderne, accélération GPU NVIDIA et métadonnées enrichies.

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
git clone https://github.com/votre-user/audiobook-manager.git
cd audiobook-manager

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
python web_ui.py

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
python main.py --source "/path/to/audiobook" --output "/path/to/output"

# Traiter tout un dossier
python main.py --source "/path/to/audiobooks" --output "/path/to/output" --all

# Options avancées
python main.py --source "/path/to/audiobook" --output "/path/to/output" \
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
audiobook-manager/
├── web_ui.py               # Interface web Flask
├── main.py                 # Point d'entrée CLI
├── audiobook_processor.py  # Logique de traitement
├── scraper.py              # Scraping web
├── config.py              # Configuration
├── requirements.txt        # Dépendances principales
├── requirements_web.txt    # Dépendances web
├── templates/
│   └── index.html         # Template web
├── static/
│   ├── css/              # Styles
│   └── js/               # Scripts
└── output/               # Fichiers M4B générés
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
python main.py --source "/path/to/audiobook" --output "/path/to/output" --verbose

# Logs dans /tmp/audiobooks/
tail -f /tmp/audiobooks/audiobook_processor.log
```

## � Développement

### Tests
```bash
# Tests unitaires
python -m pytest tests/

# Test scraping
python test.py --test-scraper

# Test GPU
python test.py --test-gpu
```

### Contribution
1. Fork le projet
2. Créer une branche `feature/nouvelle-fonctionnalite`
3. Commit les changements
4. Push et créer une Pull Request

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus d'informations.

## 📁 Archives

Les fichiers archivés et versions précédentes sont disponibles dans le dossier [Archives](./Archives/README.md).

---

## 🤝 Support

- **Issues** : [GitHub Issues](https://github.com/votre-user/audiobook-processor/issues)
- **Documentation** : [Wiki](https://github.com/votre-user/audiobook-processor/wiki)
- **Discussions** : [GitHub Discussions](https://github.com/votre-user/audiobook-processor/discussions)

## 🎉 Remerciements

- **FFmpeg** : Pour l'encodage audio
- **Google Books API** : Pour les métadonnées
- **Babelio** : Pour la littérature française
- **NVIDIA** : Pour l'accélération GPU

---

**Audiobook Processor Pro** - Transformez vos audiobooks professionnellement ! 🎧✨

## Installation

### Prérequis

```bash
# Installation des dépendances système
sudo apt update
sudo apt install ffmpeg python3-pip unrar

# Installation Python
pip install -r requirements.txt

# Installation Ollama (pour la génération de synopsis)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2
```

### Configuration

1. Copiez le dossier du projet :
```bash
cp -r scripts_audiobooks /votre/emplacement/
cd /votre/emplacement/scripts_audiobooks
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les chemins dans `config.py` si nécessaire

## Utilisation

### Traitement complet

```bash
# Traite tous les audiobooks du dossier par défaut
python main.py

# Spécifie un dossier source
python main.py --source /chemin/vers/audiobooks

# Spécifie un dossier de sortie
python main.py --output /chemin/vers/output
```

### Traitement individuel

```bash
# Traite un seul fichier
python main.py --single "Auteur - Titre.zip"

# Simulation sans conversion
python main.py --single "fichier.zip" --dry-run
```

### Options avancées

```bash
# Mode verbeux
python main.py --verbose

# Désactive le scraping
python main.py --no-scraping

# Désactive la génération IA
python main.py --no-ai

# Change le bitrate audio
python main.py --bitrate 192k

# Upload vers Audiobookshelf
python main.py --upload
```

## Structure des fichiers

```
scripts_audiobooks/
├── main.py                 # Point d'entrée principal
├── audiobook_processor.py  # Logique de traitement principal
├── scraper.py             # Scraping Babelio/FNAC
├── audiobookshelf_client.py # Client pour l'upload
├── config.py              # Configuration
├── requirements.txt       # Dépendances Python
└── README.md             # Documentation
```

## Format de sortie

Les fichiers sont renommés selon le format : `Auteur - Titre.m4b`

Les métadonnées intégrées incluent :
- Titre
- Auteur  
- Série (si applicable)
- Numéro dans la série (si applicable)
- Description
- Pochette
- Genre
- Année

## Configuration Audiobookshelf

Pour activer l'upload vers Audiobookshelf, configurez les variables suivantes dans `config.py` :

```python
audiobookshelf_host = "votre-serveur.com"
audiobookshelf_port = 13378
audiobookshelf_username = "votre-utilisateur"
audiobookshelf_password = "votre-mot-de-passe"
```

Ou utilisez des variables d'environnement :

```bash
export AUDIOBOOKSHELF_HOST="votre-serveur.com"
export AUDIOBOOKSHELF_USERNAME="votre-utilisateur"
export AUDIOBOOKSHELF_PASSWORD="votre-mot-de-passe"
```

## Formats supportés

### Fichiers d'entrée
- **Archives** : .zip, .rar, .7z
- **Audio** : .mp3, .m4a, .wav, .flac, .aac
- **Dossiers** contenant des fichiers audio

### Fichier de sortie
- **M4B** avec métadonnées et pochette intégrées

## Logging

Le système génère un fichier log `audiobook_processing.log` avec tous les détails du traitement.

## Exemples d'utilisation

### Cas 1 : Traitement complet
```bash
python main.py --source "/home/user/Mes Audiobooks" --output "/home/user/Audiobooks Nettoyés"
```

### Cas 2 : Test avec simulation
```bash
python main.py --dry-run --verbose
```

### Cas 3 : Traitement avec upload
```bash
python main.py --upload --bitrate 192k
```

## Dépannage

### Problèmes courants

1. **ffmpeg non trouvé**
   ```bash
   sudo apt install ffmpeg
   ```

2. **Ollama non disponible**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull llama2
   ```

3. **Permissions refusées**
   ```bash
   chmod +x main.py
   ```

4. **Dépendances manquantes**
   ```bash
   pip install -r requirements.txt
   ```

### Logs détaillés

Pour obtenir des logs détaillés en cas de problème :
```bash
python main.py --verbose 2>&1 | tee debug.log
```

## Architecture

Le système est modulaire et peut être étendu :

- **AudiobookProcessor** : Logique principale de traitement
- **BookScraper** : Extraction des métadonnées depuis le web
- **AudiobookshelfClient** : Interface avec Audiobookshelf
- **Config** : Gestion centralisée de la configuration

## Contribuer

Pour ajouter de nouvelles sources de scraping ou des fonctionnalités :

1. Modifiez `scraper.py` pour ajouter de nouvelles sources
2. Étendez `config.py` pour de nouvelles options
3. Ajoutez des tests dans le dossier `tests/`

## Licence

Ce projet est sous licence MIT.
