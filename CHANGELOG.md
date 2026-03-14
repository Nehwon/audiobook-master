# 📓 Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et versionnement sémantique.

## [Unreleased]

### Added
- Phase 0 UI v3 complétée: Architecture Decision Records (ADR-001, ADR-002), RFC-001 événements JSON, MVP backlog complet.
- Documentation technique exhaustive: guides développement, installation, Docker, formats audio, plugins, CI/CD.
- Architecture frontend v2.3.0 planifiée: composants React, pages modernes, migration PostgreSQL.
- Services de persistance: recovery service, endpoints API, gestion versions automatique.
- Logo professionnel: `audiobook-manager.jpg` pour documentation et branding.
- Questionnaire validation TR001: validation structurée Phase 0 avec critères GO/NO-GO.
- Analyse dysfonctionnements AN002: audit technique complet avec plan d'action prioritaire.

### Changed
- Refonte complète de la documentation: guides structurés, architecture clarifiée, planning détaillé.
- Organisation des sprints Dev v2.3.0: documentation consolidée avec runbooks et clotures.
- Mise à jour TODO.md: passage en mode sprint pilotage avec objectifs et livrables clairs.
- Simplification README.md: focus sur démarrage rapide et références documentation détaillée.

### Fixed
- Identification et documentation des dysfonctionnements critiques: ImportError Base SQLAlchemy, configuration logs, tests inopérants.
- Plan de correction prioritaire: Phase 1 (1-2 jours), Phase 2 (3-5 jours), Phase 3 (1-2 semaines).

### Deprecated
- `run.py` et `start_web.py` maintenus pour compatibilité legacy (délégation vers entrées recommandées).

### Security
- Audit des dépendances et identification des vulnérabilités potentielles.

## [3.0.0-alpha.1] - 2026-03-14 (Pré-release)

### Added
- 🏗️ Architecture v3: FastAPI + PostgreSQL + WebSocket temps réel
- 📋 Phase 0 complète: ADR, RFC, MVP backlog avec 12 user stories
- 📚 Documentation technique: 4 guides complets + architecture détaillée
- 🎯 Planning UI v3: 6 semaines réparties en 3 sprints
- 🔍 Analyse dysfonctionnements: rapport complet avec plan d'action
- 📝 Questionnaire validation: TR001 pour décisions techniques
- 🖼️ Branding: logo professionnel pour documentation

### Changed
- 📖 Refonte documentation: guides structurés et références croisées
- 🏛️ Architecture: passage de Flask à FastAPI pour backend moderne
- 🗂️ Organisation: documentation Dev v2.3.0 consolidée
- 📊 Planning: mode sprint avec objectifs clairs et livrables

### Fixed
- 🐛 Dysfonctionnements identifiés: ImportError Base SQLAlchemy, logs, tests
- 🔧 Configuration: adaptation environnement local
- 📋 Dépendances: SQLAlchemy et psycopg2 ajoutés

### Deprecated
- ⚠️ Legacy wrappers: `run.py`, `start_web.py` (compatibilité maintenue)

### Notes
- 🚀 Cette version alpha prépare la migration complète vers UI v3
- 📋 Phase 0 validée avec tous les livrables techniques
- 🎯 Prêt pour démarrage Phase 1 (Backend FastAPI)

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
