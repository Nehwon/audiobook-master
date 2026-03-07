# Changelog

Ce fichier suit une structure inspirée de *Keep a Changelog*.

## [Unreleased]

### Fixed
- Rétablissement de plusieurs chemins de compatibilité legacy dans le traitement audio (`core/processor.py`) : helpers historiques (`check_fdk_aac`, `detect_gpu_acceleration`, `add_cover_to_m4b`, `scrap_book_info`, `generate_synopsis`, `download_cover`), parsing de noms plus tolérant et normalisation de fichiers plus robuste.
- Amélioration des scrapers metadata (`core/metadata.py`) avec support de pagination simple en recherche Audible/Babelio, alias legacy `_extract_audible_length`, et téléchargement de cover plus fiable (validation URL + création de dossiers).
- Ajustement du générateur de synopsis (`ai/synopsis/generator.py`) pour rétablir l’API attendue par les tests legacy (`validate_synopsis`, prompt FR/EN compatible, fallback textuel plus stable).

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
