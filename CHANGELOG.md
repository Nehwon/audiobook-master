# 📓 Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et versionnement sémantique.

## [Unreleased]

### Added
- Sprint 6 clôturé: publication du plan d'exécution et du document de clôture (`docs/sprint-6/README.md`, `docs/sprint-6/CLOTURE.md`).
- Sprint 5 clôturé côté documentation: formalisation de l'implémentation UX « erreurs rouges + validation persistée » (`docs/sprint-5/README.md`, `docs/sprint-5/CLOTURE.md`).
- Sprint 4 clôturé côté documentation: plan de migration UI React consolidé (`docs/sprint-4/README.md`, `docs/sprint-4/CLOTURE.md`).
- Référencement du Sprint 4 dans la documentation racine (`README.md`, `ROADMAP.md`, `TODO.md`, `docs/SPRINTS_REACT_POSTGRESQL.md`).
- Référencement du Sprint 5 terminé dans la documentation racine et de pilotage (`README.md`, `ROADMAP.md`, `TODO.md`, `docs/SPRINTS_REACT_POSTGRESQL.md`).
- Référencement du Sprint 6 terminé dans la documentation racine et de pilotage (`README.md`, `ROADMAP.md`, `TODO.md`, `docs/SPRINTS_REACT_POSTGRESQL.md`).

### Changed
- Mise à jour de l'état d'avancement des sprints: Sprint 6 est désormais marqué comme terminé.
- Mise à jour de l'état d'avancement des sprints: Sprint 5 est désormais marqué comme terminé (périmètre documentaire).
- Mise à jour de l'état d'avancement des sprints: Sprint 4 est désormais marqué comme terminé (périmètre documentaire).
- Harmonisation éditoriale des documents de pilotage produit et de migration frontend.

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
