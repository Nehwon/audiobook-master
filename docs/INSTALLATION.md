# 🚀 Installation

## Prérequis

- Python 3.10+
- `ffmpeg` dans le `PATH`
- (Optionnel) `ollama` pour synopsis IA

## Installation locale

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Vérification rapide

```bash
python -m core.main --diagnostic
pytest -q tests/test_smoke_suite.py
```

## Démarrage

```bash
# CLI
python -m core.main --source ./data/source --output ./data/output

# Web
python -m web.app
```

## Variables utiles

| Variable | Exemple |
|---|---|
| `AUDIOBOOK_MEDIA_DIR` | `/app/data/source` |
| `AUDIOBOOK_OUTPUT_DIR` | `/app/data/output` |
| `AUDIOBOOK_TEMP_DIR` | `/tmp/audiobooks_web` |
| `AUDIOBOOK_LOG_DIR` | `/app/logs` |
| `AUDIOBOOK_LOG_PROFILE` | `debug-conversion` |

## Docker

Voir `docs/docker-setup.md` pour la configuration complète (`docker compose up -d`).
