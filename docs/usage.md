# Utilisation détaillée

Ce document centralise les détails d'usage (CLI, Web, Docker et tests) pour garder le `README.md` concis.

## CLI (entrée recommandée)

Entrée principale : `core/main.py`

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

### Variables d'environnement Audiobookshelf (CLI)

```text
AUDIOBOOKSHELF_HOST
AUDIOBOOKSHELF_PORT
AUDIOBOOKSHELF_USERNAME
AUDIOBOOKSHELF_PASSWORD
AUDIOBOOKSHELF_TOKEN
AUDIOBOOKSHELF_LIBRARY_ID
```

## Interface Web

Lancement :

```bash
python -m web.app
```

Variables d'environnement dossiers :

- `AUDIOBOOK_MEDIA_DIR` (fallback `SOURCE_DIR`, puis `/app/data/source`)
- `AUDIOBOOK_OUTPUT_DIR` (fallback `OUTPUT_DIR`, puis `/app/data/output`)
- `AUDIOBOOK_TEMP_DIR` (fallback `TEMP_DIR`, puis `/tmp/audiobooks_web`)
- `AUDIOBOOK_LOG_DIR` (fallback `LOG_DIR`, puis `/app/logs`)

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

## Docker

Démarrage rapide :

```bash
docker compose up -d
```

Avec monitoring :

```bash
docker compose --profile monitoring up -d
```

Voir aussi : `docs/docker-setup.md`.

## Tests

Suite complète :

```bash
pytest -q
```

Validation ciblée (exemples) :

```bash
pytest tests/test_web_api.py -q
pytest tests/test_smoke_suite.py -q
```

## Limites connues

- Les scripts legacy `run.py` et `start_web.py` sont conservés pour compatibilité et affichent un avertissement de dépréciation.
- Les fonctionnalités IA dépendent d'Ollama et d'un modèle local disponible.
