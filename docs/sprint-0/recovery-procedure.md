# Sprint 0 — Procédure de reprise automatique au démarrage

## Objectif

Au boot de l'application, réconcilier l'état des jobs et reprendre automatiquement les traitements interrompus lorsque c'est sûr.

## Algorithme de recovery (version cible)

1. Charger tous les jobs `running` ou `retry_pending` depuis PostgreSQL.
2. Détecter les jobs orphelins:
   - aucun heartbeat depuis `timeout_running`.
3. Pour chaque job orphelin:
   - si étape idempotente/retryable -> `retry_pending` + incrément tentatives,
   - sinon -> `failed` avec erreur `MANUAL_INTERVENTION_REQUIRED`.
4. Replanifier les jobs `retry_pending` selon politique de backoff.
5. Publier événements `job.updated` / `job.failed` dans `outbox_event`.
6. Exposer un résumé de réconciliation via `/api/recovery/status`.

## Politique de retry (proposée)

- `max_attempts`: 3
- `backoff_seconds`: 15, 60, 180
- `retryable_errors`: erreurs I/O transitoires, timeouts externes
- `non_retryable_errors`: données invalides, corruption archive, violations métier

## Sécurité d'exécution

- Verrou logique par `job_id` pour éviter doubles workers.
- Idempotence des étapes critiques (pas de double création de sortie finale).
- Journal d'audit `recovery_run_id` pour traçabilité.

## Critères de validation opérationnelle

- Crash simulé en plein traitement -> reprise sans action manuelle pour les cas retryables.
- Aucune duplication d'artefacts de sortie pour un même job.
- Les erreurs non retryables restent visibles et actionnables en UI.
