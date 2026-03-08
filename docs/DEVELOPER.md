# 🛠️ Guide développeur

## Vue d'ensemble

Le projet est organisé autour de deux entrées runtime :

- `python -m core.main` (CLI)
- `python -m web.app` (API + UI Flask)

Wrappers legacy maintenus : `run.py`, `start_web.py`.

## Structure

```text
core/           logique métier conversion + config + metadata + diagnostics
web/            application Flask (routes API)
templates/      interface HTML
integrations/   client Audiobookshelf
plugins/        plugins metadata/covers/exports
tests/          tests unitaires/intégration/smoke
docs/           documentation projet
```

## Parcours de dev local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q tests/test_smoke_suite.py
```

## Tests

### Cibles principales

- `tests/test_smoke_suite.py` : socle minimal.
- `tests/test_web_api.py`, `tests/test_web_rename.py`, `tests/test_web_ollama.py` : API web.
- `tests/test_processor*.py` : pipeline audio.
- `tests/test_metadata*.py` : scraping/enrichissement.
- `tests/test_*plugins*.py` : architecture plugins.

## Conventions runtime

- Préférer les exécutions module (`python -m ...`) plutôt que scripts legacy.
- Éviter d'introduire de nouveaux defaults machine-spécifiques.
- Centraliser les valeurs dans `ProcessingConfig` et les env vars.

## Débogage

```bash
# Diagnostic environnement
python -m core.main --diagnostic

# Diagnostic JSON exploitable CI
python -m core.main --diagnostic-json

# Logs verbeux conversion
python -m core.main --log-profile debug-conversion -v
```

## Zones sensibles

- `web/app.py` : fichier volumineux, toucher par blocs isolés + tests API ciblés.
- `core/processor.py` : conserver compatibilité des helpers legacy couverts par tests.
- `integrations/audiobookshelf.py` : attention aux erreurs réseau et auth.
