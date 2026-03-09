# Sprint 1 — Fondations PostgreSQL (implémentation initiale)

Ce sprint introduit une base de persistance transactionnelle pour les états de traitement.

## Livrables implémentés

- Couche `persistence/` avec:
  - connexion DB (`db.py`),
  - modèles SQLAlchemy (`models.py`),
  - repositories (`repositories.py`),
  - service transactionnel (`service.py`).
- Migration SQL versionnée: `database/migrations/0001_sprint1_foundations.sql`.
- Bootstrap local: `scripts/bootstrap_postgres.sh`.
- Script d'init PostgreSQL Docker: `database/init.sql`.
- Intégration du service transactionnel dans les endpoints/jobs web:
  - création persistée (`/api/jobs/enqueue`, `/api/jobs/reprocess`),
  - transitions persistées (`running`, `done`, `failed`, `cancelled`),
  - endpoint d'annulation `POST /api/jobs/cancel`.

## Dépendances

- Dépendances optionnelles PostgreSQL/ORM: `requirements_postgresql.txt`

## Variables d'environnement

- `AUDIOBOOK_DATABASE_URL` (ex: `postgresql://audiobook:audiobook123@postgres:5432/audiobook_manager`)

## Prochaine étape

Étendre la persistance au niveau fin des étapes (`processing_step`) et des résultats de
validation (`validation_result`) pour préparer la reprise automatique du Sprint 2.
