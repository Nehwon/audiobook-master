# Sprint 2 — Reprise automatique et résilience

## Objectif

Automatiser la reprise après interruption, éviter les doubles traitements et améliorer la robustesse de l'exécution.

## Statut

Terminé.

## Périmètre

- Recovery automatique au démarrage.
- Politique de retry configurable.
- Verrous/idempotence sur les traitements.
- Visibilité admin de la reprise.

## Plan d'implémentation

### Lot 1 — Heartbeat & détection d'orphelins

- Ajouter un heartbeat sur les jobs en exécution.
- Introduire un timeout de job sans heartbeat.
- Identifier au boot les jobs `running` orphelins.

### Lot 2 — Recovery orchestration

- Définir la politique de reprise:
  - `retry_pending` pour les jobs retryables,
  - état terminal + alerte pour intervention manuelle sinon.
- Journaliser chaque décision de reprise (audit trail).

### Lot 3 — Retry policy

- Ajouter paramètres de retry (max tentatives, backoff).
- Appliquer la politique selon le type d'étape / type d'erreur.
- Empêcher dépassement de tentatives via garde-fous repository/service.

### Lot 4 — Idempotence & verrouillage

- Ajouter clé d'idempotence par job/dossier/étape.
- Implémenter verrouillage applicatif ou DB pour éviter exécutions concurrentes d'un même job logique.
- Garantir absence de doublons de sortie.

### Lot 5 — Exposition & monitoring

- Ajouter endpoint admin `/api/recovery/status`.
- Exposer compteurs utiles:
  - jobs repris automatiquement,
  - jobs en échec nécessitant action,
  - retries en cours.

## Backlog détaillé

- [x] Implémenter heartbeat périodique côté worker/job runner.
- [x] Ajouter colonnes de suivi (`last_heartbeat_at`, `retry_count`, `recovery_status`) si nécessaire.
- [x] Mettre à jour la couche de persistance et migrations associées.
- [x] Implémenter le service de recovery au démarrage applicatif.
- [x] Ajouter endpoint `/api/recovery/status`.
- [x] Écrire tests d'intégration crash/restart.
- [x] Écrire tests d'idempotence (pas de doublon d'outputs).
- [x] Documenter runbook de reprise manuelle minimale.

## Critères d'acceptation

- Après crash simulé, reprise automatique pour les cas retryables.
- Aucune duplication de traitement pour un même job logique.
- Visibilité admin claire sur l'état de recovery.
- Journal d'audit exploitable pour analyse post-incident.

## Risques & mitigation

- Risque de faux positifs d'orphelins (heartbeat trop agressif).
  - Mitigation: timeout configurable + marge de sécurité.
- Risque de contention de verrous.
  - Mitigation: granularité de verrou par job logique + timeout de lock.
- Risque de logique retry inadaptée aux erreurs métier.
  - Mitigation: taxonomie d'erreurs + table de décision retryable/non-retryable.

## Définition de terminé (DoD)

- Code, migration et tests d'intégration mergés.
- Documentation API et exploitation mises à jour.
- Démonstration crash/restart validée sur environnement Docker local.


## Artefacts de clôture

- Runbook: `docs/sprint-2/RUNBOOK.md`
- Clôture: `docs/sprint-2/CLOTURE.md`
