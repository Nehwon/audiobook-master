# 📓 Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et versionnement sémantique.

## [Unreleased]

### Added
- Sprint 3 finalisé: nouveaux endpoints frontend `GET /api/folders/errors`, `GET /api/folders/validations` et flux SSE `GET /api/events/stream`.
- Contrat OpenAPI minimal Sprint 3 (`docs/api/openapi-frontend-sprint3.yaml`).
- Tests de contrat API Sprint 3 (`tests/test_web_api_sprint3.py`).

### Changed
- Mise à jour de la documentation racine (`README.md`, `ROADMAP.md`, `TODO.md`) pour refléter l'état réel du projet.
- Mise à jour des documents dans `docs/` (usage, installation, développeur, CI/CD, Docker, plugins, frontend).
- Harmonisation éditoriale (structure, tableaux, sections d'avancement, terminologie CLI/Web).

### Notes
- Les wrappers `run.py` et `start_web.py` sont maintenus pour compatibilité, mais restent dépréciés.

## [2.1.2] - Référence historique

### Added
- Consolidation API web (jobs, monitor, outputs, routes Audiobookshelf packets/scheduler).
- Commandes diagnostics CLI et profil de logs conversion.
- Couverture tests sur processor/metadata/web/plugins/integrations.

### Changed
- Documentation centralisée dans `docs/` et simplification du README.
- Clarification des points d'entrée recommandés (`python -m core.main`, `python -m web.app`).

### Fixed
- Rétablissements de compatibilité legacy dans le pipeline processor/metadata/synopsis.
