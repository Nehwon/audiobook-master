# Clôture Sprint 2 — Reprise automatique et résilience

## Résumé

Sprint 2 est clôturé avec les livrables suivants:

- Heartbeat périodique des jobs en cours.
- Détection de jobs `running` orphelins au démarrage.
- Recovery orchestration (`retry_pending` vs `manual_intervention`).
- Audit trail des décisions de recovery.
- Contrôle d'idempotence par dossier (clé logique) pour éviter les doublons.
- Endpoint admin de monitoring: `GET /api/recovery/status`.
- Tests ciblés crash/restart et idempotence.
- Runbook opérationnel minimal.

## Validation

- Recovery au boot validé par tests Sprint 2.
- Non-régression API de base validée par tests ciblés web.
- Documentation de sprint et documentation générale mises à jour.

## Post-sprint

Points restant pour sprint suivant:

- Backoff différencié par type d'erreur.
- Exposition plus fine des métriques recovery (latence, histogrammes retry).
- Démo de reprise sur environnement Docker de validation.
