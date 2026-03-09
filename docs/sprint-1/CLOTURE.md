# Sprint 1 — Clôture

## Statut

Sprint 1 terminé et validé.

## Objectif initial

Mettre en place les fondations PostgreSQL pour persister les états de traitement et préparer la reprise automatique.

## Réalisations

- Intégration d'une couche de persistance transactionnelle (`persistence/db.py`, `persistence/models.py`, `persistence/repositories.py`, `persistence/service.py`).
- Ajout d'une migration SQL initiale (`database/migrations/0001_sprint1_foundations.sql`).
- Ajout des scripts d'initialisation PostgreSQL (`database/init.sql`, `scripts/bootstrap_postgres.sh`).
- Intégration de la persistance dans les flux web de gestion des jobs:
  - création (`/api/jobs/enqueue`, `/api/jobs/reprocess`),
  - transitions (`running`, `done`, `failed`, `cancelled`),
  - annulation (`POST /api/jobs/cancel`).

## Validation

- Schéma PostgreSQL initial disponible et versionné.
- États de jobs persistés et consultables après redémarrage.
- Erreurs métier/techniques historisées par job/dossier.

## Dette résiduelle / suites

- Compléter la persistance détaillée au niveau de certaines étapes fines (`processing_step`) selon les besoins de reprise avancée.
- Structurer l'observabilité de reprise (heartbeat + audit) dans Sprint 2.

## Décision de fin de sprint

Sprint 1 clôturé, passage en Sprint 2 autorisé.
