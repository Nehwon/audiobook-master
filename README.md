# Audiobook Master

Audiobook Master est un projet Python qui convertit des dossiers de pistes audio (`.mp3`, `.m4a`, `.flac`, etc.) en fichiers `.m4b`, avec une interface web Flask, une CLI, et une intégration optionnelle avec Audiobookshelf.

> ⚠️ **État du dépôt** : le projet contient des composants historiques (`run.py`, `start_web.py`) et des composants actifs (`core/`, `web/`, `integrations/`). Cette documentation décrit explicitement le chemin recommandé aujourd’hui.

## 1) Fonctionnalités actuelles

### Conversion audio
- Traitement d’un dossier livre vers un fichier `.m4b`.
- Gestion de plusieurs extensions audio (définies dans `core/config.py`).
- Paramètres audio configurables (bitrate, sample rate, normalisation loudnorm, compresseur, chapitres).
- Détection de structures de dossiers invalides (par ex. sous-dossiers imbriqués non attendus).

### Interface web (`web/app.py`)
- Exploration de la bibliothèque source.
- Validation/extraction d’archives.
- Renommage de dossiers (avec overrides manuels).
- Mise en file de jobs, suivi des jobs et consultation des logs.
- Configuration web persistée dans un JSON local.
- Endpoints dédiés à Ollama (statut/pull/delete/search) pour l’assistance IA.
- Endpoints de santé et de monitoring (`/health`, `/api/monitor`).

### Intégration Audiobookshelf
- Authentification (token direct ou login/password).
- Upload d’un `.m4b` vers une bibliothèque.
- Déclenchement d’un scan de bibliothèque après upload.
- Sélection explicite de bibliothèque via `AUDIOBOOKSHELF_LIBRARY_ID` ou `--abs-library-id`.

## 2) Architecture du dépôt

- `core/` : logique de traitement audio, config, métadonnées, CLI principale.
- `web/` + `templates/` : application Flask et UI.
- `integrations/` : client Audiobookshelf et synchronisation.
- `tests/` : suite de tests Python (volumineuse, hétérogène).
- `docs/` : documentation technique complémentaire (installation, docker, CI/CD, dev).
- `docker-compose.yml` + `Dockerfile` : exécution conteneurisée.

## 3) Prérequis

### Runtime
- Python 3.10+ recommandé.
- `ffmpeg` installé et disponible dans le `PATH`.
- Dépendances Python de `requirements.txt`.

### Dépendances système utiles
- `ffprobe` (souvent fourni avec ffmpeg).
- Outils d’archives selon l’usage (`unzip`, support `rarfile` côté Python).

## 4) Installation locale (recommandée)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Vérification rapide :

```bash
python -c "import flask, requests, mutagen; print('ok')"
ffmpeg -version
```

## 5) Utilisation CLI (chemin recommandé)

L’entrée CLI moderne est `core/main.py`.

### Exemple minimal

```bash
python -m core.main --source /chemin/source --output /chemin/output
```

### Options principales

```text
--source / -s          Dossier source
--output / -o          Dossier de sortie
--single / -f          Traiter un fichier spécifique
--dry-run / -n         Simulation sans conversion
--upload / -u          Upload vers Audiobookshelf après traitement
--abs-token            Token API Audiobookshelf (prioritaire)
--abs-library-id       Bibliothèque Audiobookshelf cible
--no-scraping          Désactive le scraping de métadonnées
--no-synopsis|--no-ai  Désactive la génération IA
--bitrate / -b         Bitrate (ex: 64k, 128k, 192k)
--samplerate           Fréquence d'échantillonnage
--no-chapters          Désactive le chapitrage
--no-normalization     Désactive loudnorm
--no-compression       Désactive compresseur
--no-gpu               Désactive accélération GPU
--aac-coder            twolo|fast
--verbose / -v         Logs détaillés
```

Variables d'environnement Audiobookshelf supportées par la CLI :

```text
AUDIOBOOKSHELF_HOST
AUDIOBOOKSHELF_PORT
AUDIOBOOKSHELF_USERNAME
AUDIOBOOKSHELF_PASSWORD
AUDIOBOOKSHELF_TOKEN
AUDIOBOOKSHELF_LIBRARY_ID
```

## 6) Utilisation Web

### Lancer l’application

```bash
python -m web.app
```

Par défaut, l’application lit des variables d’environnement pour ses dossiers de travail :
- `AUDIOBOOK_MEDIA_DIR` (fallback `SOURCE_DIR`, puis `/app/data/source`)
- `AUDIOBOOK_OUTPUT_DIR` (fallback `OUTPUT_DIR`, puis `/app/data/output`)

### Endpoints principaux

- `GET /` : interface HTML.
- `GET /api/library` : inventaire des dossiers source.
- `POST /api/archive/validate` : validation d’archive.
- `POST /api/extract` : extraction d’archive.
- `POST /api/rename` : renommage de dossiers.
- `POST /api/jobs/enqueue` : création de jobs.
- `GET /api/jobs` : état des jobs.
- `GET /api/logs` : logs applicatifs.
- `GET /api/config` / `POST /api/config` : lecture/écriture config web.
- `GET /api/ollama/status` : état du service Ollama.
- `GET /health` : endpoint santé.

## 7) Exécution Docker

### Démarrage rapide

```bash
docker compose up -d
```

Services déclarés dans le compose :
- `audiobook-manager` (app principale)
- `ollama` (LLM local)
- `prometheus` (profil `monitoring`)
- `grafana` (profil `monitoring`)
- `postgres` (profil `database`)
- `redis` (profil `cache`)

### Avec monitoring

```bash
docker compose --profile monitoring up -d
```

## 8) Tests

Lancer toute la suite :

```bash
pytest -q
```

> Remarque : la suite actuelle est importante et certaines classes de tests peuvent être instables selon l’environnement/localisation du code. Utiliser des sous-ensembles (`pytest tests/test_web_api.py -q`) pour des validations ciblées.

## 9) Limites / points d’attention connus

- Le dépôt contient des chemins “legacy” (`run.py`, `start_web.py`) qui ne reflètent pas toujours la structure active.
- La documentation historique mentionnait des promesses non vérifiables (couverture 100%, production-ready universel). Elles ont été retirées ici au profit d’un état factuel.
- Certaines fonctionnalités IA dépendent d’Ollama et d’un modèle disponible localement.

## 10) Références internes

- Documentation d’installation détaillée : `docs/INSTALLATION.md`
- Mise en place Docker : `docs/docker-setup.md`
- Guide développeur : `docs/DEVELOPER.md`
