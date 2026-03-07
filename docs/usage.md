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

Dans l'UI web, la configuration Audiobookshelf inclut aussi `audiobookshelf_library_id` (préservé dans `/api/config`).

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


## Onglet Plugins

Onglet `Plugins` (UI web) : permet d'activer/désactiver les plugins metadata/covers/exports et de sauvegarder leur configuration dans `web_config.json`.

Configuration des plugins (source de métadonnées) sous forme de tableau :

| Plugin | Clé de configuration | Valeur par défaut | Description |
|---|---|---|---|
| `google_books` | `scraping_sources` (CLI/Web config) | activé | Recherche via API Google Books (priorité 1). |
| `audible` | `scraping_sources` (CLI/Web config) | activé | Recherche spécialisée audiobook (priorité 2). |
| `babelio` | `scraping_sources` (CLI/Web config) | activé | Fallback francophone (priorité 3). |

Exemple de configuration (ordre = fallback) :

```json
{
  "scraping_sources": ["google_books", "audible", "babelio"]
}
```

Si un plugin est retiré de `scraping_sources`, il ne sera pas utilisé pendant l'enrichissement des métadonnées.


### Structure du dossier `plugins/`

```text
plugins/
  metadata/
    base_scraper.py
    scraper_google_books.py
    scraper_audible.py
    scraper_babelio.py
  covers/
    base_cover.py
    provider_existing_file.py
    provider_url_download.py
  exports/
    base_export.py
    export_audiobookshelf.py
```

### Plugins covers (tableau)

| Plugin | Fichier | Configuration principale | Description |
|---|---|---|---|
| `existing_file` | `plugins/covers/provider_existing_file.py` | `cover_sources` | Réutilise `metadata.cover_path` si le fichier existe. |
| `url_download` | `plugins/covers/provider_url_download.py` | `cover_sources` | Télécharge la cover depuis `metadata.cover_url`. |

### Plugins d'export (tableau)

| Plugin | Fichier | Configuration principale | Description |
|---|---|---|---|
| `audiobookshelf` | `plugins/exports/export_audiobookshelf.py` | `library_id` | Exporte un `.m4b` vers Audiobookshelf via le client configuré. |

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
