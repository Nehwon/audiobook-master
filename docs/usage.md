# 🧭 Utilisation (CLI + Web)

## 1) CLI (entrée recommandée)

```bash
python -m core.main --source /chemin/source --output /chemin/output
```

### Options principales

| Option | Description |
|---|---|
| `--source`, `-s` | Dossier source |
| `--output`, `-o` | Dossier de sortie |
| `--single`, `-f` | Traiter un seul fichier/dossier |
| `--dry-run`, `-n` | Simulation sans conversion |
| `--upload`, `-u` | Upload Audiobookshelf après traitement |
| `--abs-token` | Token API Audiobookshelf |
| `--abs-library-id` | ID de bibliothèque Audiobookshelf |
| `--no-scraping` | Désactive scraping métadonnées |
| `--no-synopsis` / `--no-ai` | Désactive synopsis IA |
| `--bitrate`, `-b` | Bitrate cible (ex: `96k`, `128k`) |
| `--samplerate` | Échantillonnage (Hz) |
| `--no-chapters` | Désactive chapitrage auto |
| `--no-normalization` | Désactive loudnorm |
| `--no-compression` | Désactive compresseur |
| `--no-gpu` | Désactive accélération GPU |
| `--aac-coder` | `twolo` ou `fast` |
| `--diagnostic` | Rapport diagnostic humain |
| `--diagnostic-json` | Rapport diagnostic JSON |
| `--log-profile` | `standard` ou `debug-conversion` |

### Exemples

```bash
# Diagnostic rapide
python -m core.main --diagnostic

# Conversion avec logs détaillés
python -m core.main --source ./data/source --output ./data/output --log-profile debug-conversion -v

# Conversion + upload Audiobookshelf
python -m core.main --source ./data/source --output ./data/output --upload --abs-token "$AUDIOBOOKSHELF_TOKEN" --abs-library-id "$AUDIOBOOKSHELF_LIBRARY_ID"
```

## 2) Web

```bash
python -m web.app
```

Application exposée par défaut sur `http://localhost:5000`.

### Endpoints clés

| Méthode | Endpoint | Rôle |
|---|---|---|
| `GET` | `/` | UI principale |
| `GET` | `/api/library` | Inventaire source |
| `POST` | `/api/archive/validate` | Validation archive |
| `POST` | `/api/extract` | Extraction archive |
| `POST` | `/api/rename` | Renommage dossier |
| `POST` | `/api/jobs/enqueue` | Créer jobs conversion |
| `GET` | `/api/jobs` | Suivi jobs |
| `GET` | `/api/monitor` | Signatures d'état |
| `GET` | `/api/outputs` | Liste sorties `.m4b` |
| `GET` | `/api/download/<filename>` | Téléchargement sortie |
| `GET` | `/health` | Santé service |

### Intégration Audiobookshelf (web)

Routes disponibles sous `/api/integrations/audiobookshelf/...` :
- gestion packets,
- metadata,
- changelog,
- soumission,
- scheduling,
- diffusion,
- nettoyage.

## 3) Variables d'environnement utiles

| Variable | Usage |
|---|---|
| `AUDIOBOOK_MEDIA_DIR` | Source web (prioritaire) |
| `AUDIOBOOK_SOURCE_DIR` | Alias compatibilité source web |
| `SOURCE_DIR` | Variable legacy source web |
| `AUDIOBOOK_OUTPUT_DIR` | Sortie web |
| `AUDIOBOOK_TEMP_DIR` | Temp web |
| `AUDIOBOOK_LOG_DIR` | Logs web |
| `AUDIOBOOK_LOG_PROFILE` | Profil logs CLI |
| `AUDIOBOOKSHELF_*` | Paramètres intégration Audiobookshelf |
