# Audiobook Master

<div align="center">

[![Audiobook Master](https://github.com/Nehwon/audiobook-master/raw/main/docs/logo.png)

</div>

Audiobook Master convertit des dossiers de pistes audio (`.mp3`, `.m4a`, `.flac`, etc.) en fichiers `.m4b`, avec une CLI Python, une interface web Flask et une intégration optionnelle Audiobookshelf.

> ℹ️ Compatibilité : `run.py` et `start_web.py` sont conservés comme wrappers legacy et délèguent vers les entrées recommandées `python -m core.main` et `python -m web.app`.

## Démarrage rapide

### Prérequis
- Python 3.10+
- `ffmpeg` dans le `PATH`
- Dépendances Python : `requirements.txt`

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Exécution

```bash
python -m core.main --source /chemin/source --output /chemin/output
python -m web.app
```

## Architecture (résumé)

- `core/` : logique de traitement audio, config, métadonnées, CLI.
- `web/` + `templates/` : application Flask et UI.
- `integrations/` : client Audiobookshelf et synchronisation.
- `docs/` : documentation détaillée.
- `tests/` : tests automatisés.

## Documentation détaillée

- Utilisation détaillée (CLI/Web/Docker/Tests) : `docs/usage.md`
- Matrice formats audio supportés : `docs/audio-format-matrix.md`
- Installation complète : `docs/INSTALLATION.md`
- Docker : `docs/docker-setup.md`
- Développeur : `docs/DEVELOPER.md`

## Validation rapide

```bash
pytest -q tests/test_smoke_suite.py
```
