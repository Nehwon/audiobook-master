# Changelog

Ce fichier suit une structure inspirée de *Keep a Changelog*.

## [Unreleased]

### Changed
- Refonte complète de la documentation Markdown à la racine pour décrire l’état réel du dépôt (README, roadmap, TODO).
- Clarification des chemins d’exécution recommandés (`python -m core.main` et `python -m web.app`) et distinction avec les scripts legacy.
- Nettoyage des affirmations non vérifiables (ex: promesses de couverture “100%” et statut production généralisé).

## [2.1.2] - État historique (référentiel)

> Cette version est conservée comme repère historique dans le dépôt. Les détails exhaustifs antérieurs étaient très verbeux et mélangeaient fonctionnalités actives, plans, et hypothèses.

### Contenu notable
- Base CLI dans `core/`.
- Interface web Flask dans `web/`.
- Intégration Audiobookshelf dans `integrations/`.
- Fichiers Docker (`Dockerfile`, `docker-compose.yml`).
- Suite de tests Python étendue dans `tests/`.

---

## Convention de version

- `MAJOR` : rupture d’API ou changement majeur de workflow.
- `MINOR` : ajout rétrocompatible de fonctionnalités.
- `PATCH` : correction ou amélioration mineure sans rupture.
