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
