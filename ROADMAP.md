# 🗺️ Roadmap produit (alignée code actuel)

Cette roadmap reflète l'état du dépôt tel qu'implémenté aujourd'hui, avec une trajectoire réaliste.

## ✅ Déjà en place

- Pipeline CLI stable avec diagnostics (`--diagnostic`, `--diagnostic-json`).
- Interface web Flask avec gestion des jobs, extraction d'archives, renommage et monitoring.
- Intégration Audiobookshelf (packets, scheduling, diffusion, nettoyage).
- Architecture plugins (metadata, covers, exports).
- Base de tests étendue + smoke suite dédiée.

## ✅ Sprint 2 finalisé

- Reprise automatique au démarrage avec audit des décisions.
- Heartbeat jobs + timeout de détection d'orphelins.
- Endpoint admin `/api/recovery/status` pour visibilité exploitation.
- Idempotence dossier logique pour limiter les doublons de traitement.

## ✅ Sprint 3 finalisé

- Endpoints frontend normalisés pour erreurs/validations (`ok`, `data`, `meta`).
- Flux SSE `/api/events/stream` branché sur outbox events (avec fallback mémoire).
- Pagination/filtrage API pour dossiers et historique.
- Contrat OpenAPI minimal + tests de contrat API dédiés.


## ✅ Sprint 4 clôturé (documentation de migration UI React)

- Cadrage final de la migration UI React consolidé.
- Parcours prioritaire "Dossiers" documenté pour implémentation.
- Stratégie SSE retenue pour synchronisation temps réel frontend.
- Passage vers Sprint 5 validé.

## ✅ Sprint 5 clôturé (erreurs rouges + validation persistée — documentation)

- Spécification UX validée pour signalisation rouge des dossiers en erreur.
- Cadrage des messages d’erreur actionnables dans la zone « Dossiers ».
- Réutilisation des validations persistées explicitée côté interface.
- Passage vers Sprint 6 validé.

## 🎯 Court terme (0–1 mois)

- **Stabiliser la CI sur un socle vert**
  - Maintenir `tests/test_smoke_suite.py` comme garde-fou.
  - Isoler les tests fragiles et normaliser les fixtures.
- **Industrialiser l'implémentation React (Sprint 6)**
  - Transformer le cadrage Sprint 5 en backlog UI exécutable et stable.
  - Prioriser les composants "erreur visible" et "validation réutilisée".
- **Durcir la couche API web**
  - Uniformiser les codes/structures d'erreurs sur tous les endpoints.

## 🔧 Moyen terme (1–3 mois)

- **Conversion audio**
  - Harmoniser les stratégies FFmpeg et les retours erreurs.
  - Fiabiliser davantage chapitres + métadonnées sur cas limites.
- **Observabilité**
  - Enrichir `/api/monitor` (métriques de file, durée moyenne jobs, erreurs récentes).
  - Structurer les logs par composant (web, processor, integrations).
- **Configuration**
  - Clarifier la hiérarchie env/fichier/défaut.
  - Mieux documenter les valeurs sensibles et leur chiffrement côté web config.

## 🚀 Long terme (3+ mois)

- **Convergence architecture**
  - Réduire les chemins legacy restants.
  - Encapsuler complètement les intégrations externes derrière interfaces plugin.
- **Qualité release**
  - Définir une routine release automatisée (tests + changelog + versioning).
  - Renforcer les checks de sécurité et de qualité (lint/typecheck si activés).


## 📌 Plan de transformation React + PostgreSQL

- Un plan de sprints détaillé est disponible dans `docs/SPRINTS_REACT_POSTGRESQL.md`.

## ❌ Hors périmètre immédiat

- Refonte totale UI.
- Migration vers un autre framework web.
- Changement majeur de stack tant que la stabilité test n'est pas consolidée.
