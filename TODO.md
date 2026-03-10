# ✅ TODO d'avancement (état actuel)

## Sprint A — Socle runtime & diagnostics (terminé)

- [x] Entrées officielles module (`core.main`, `web.app`) documentées.
- [x] Wrapper legacy `run.py`/`start_web.py` maintenus.
- [x] Commandes diagnostics CLI (`--diagnostic`, `--diagnostic-json`).
- [x] Profil de logs `debug-conversion` activable par option ou variable env.

## Sprint B — Flux web opérationnel (terminé)

- [x] Inventaire bibliothèque source (`/api/library`).
- [x] Validation/extraction archives (`/api/archive/validate`, `/api/extract`).
- [x] Renommage avec protections collisions (`/api/rename`).
- [x] Enqueue + suivi jobs (`/api/jobs/enqueue`, `/api/jobs`).
- [x] Gestion review bin/reprocess (`/api/jobs/review`, `/api/jobs/reprocess`).

## Sprint C — Intégration Audiobookshelf (terminé)

- [x] CRUD packets Audiobookshelf.
- [x] Édition/scraping metadata packet.
- [x] Changelog draft + édition manuelle.
- [x] Planification publication (`/schedule`) + exécution immédiate.
- [x] Diffusion canaux (Discord, Telegram, WhatsApp, email).
- [x] Nettoyage post-publication.

## Sprint D — Plugins (en cours)

- [x] Contrat plugins metadata/covers/exports en place.
- [x] Tests plugins metadata/covers/export présents.
- [ ] Marketplace plugins complet (UX + sécurité + signature).
- [ ] Documentation d'exploitation plugin multi-environnements.

## Sprint E — Qualité continue (en cours)

- [x] Smoke suite dédiée.
- [x] Tests API web ciblés.
- [ ] Pipeline CI strictement vert sur toute la suite.
- [ ] Normalisation lint/typecheck et seuils couverture.


## Sprint F — Résilience & recovery (terminé)

- [x] Heartbeat et timeout d'orphelin.
- [x] Recovery bootstrap (`retry_pending` / `manual_intervention`).
- [x] Endpoint `/api/recovery/status`.
- [x] Idempotence active par dossier logique.
- [x] Tests crash/restart + idempotence.
- [x] Runbook d'exploitation Sprint 2.

## Sprint G — API temps réel + contrat frontend (terminé)

- [x] Introduire schémas de réponse unifiés (`ok`, `data`, `meta`) sur endpoints frontend Sprint 3.
- [x] Ajouter endpoint erreurs par dossier (`/api/folders/errors`).
- [x] Ajouter endpoint validations déjà faites (`/api/folders/validations`).
- [x] Brancher outbox events vers SSE (`/api/events/stream`).
- [x] Ajouter tests contrat API Sprint 3 (`tests/test_web_api_sprint3.py`).
- [x] Publier une documentation OpenAPI minimale (`docs/api/openapi-frontend-sprint3.yaml`).



## Sprint H — Migration UI React (documentation) (terminé)

- [x] Consolider les artefacts de migration UI React dans `docs/`.
- [x] Formaliser le périmètre prioritaire "Dossiers" pour implémentation.
- [x] Valider les dépendances API/SSE nécessaires côté frontend.
- [x] Publier la clôture de sprint (`docs/sprint-4/CLOTURE.md`).


## Sprint I — Erreurs rouges + validation persistée (documentation) (terminé)

- [x] Formaliser le mapping fonctionnel `error_code -> message utilisateur` dans la documentation de sprint.
- [x] Spécifier le composant cible `FolderErrorBanner` et son comportement.
- [x] Cadrer le tri/filtre « dossiers en erreur » pour implémentation frontend.
- [x] Définir l’indicateur « validation réutilisée » dans le rendu dossier.
- [x] Publier la clôture de sprint (`docs/sprint-5/CLOTURE.md`).

## Sprint J — Stabilisation + mise en production (terminé)

- [x] Finaliser le plan de sprint 6 (`docs/sprint-6/README.md`).
- [x] Clôturer le sprint 6 (`docs/sprint-6/CLOTURE.md`).
- [x] Mettre à jour le plan macro des sprints (`docs/SPRINTS_REACT_POSTGRESQL.md`).
