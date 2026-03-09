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

## Dépendances

- Dépendances optionnelles PostgreSQL/ORM: `requirements_postgresql.txt`

## Variables d'environnement

- `AUDIOBOOK_DATABASE_URL` (ex: `postgresql://audiobook:audiobook123@postgres:5432/audiobook_manager`)

## Prochaine étape

Brancher `ProcessingStateService` dans le flux de traitement web/worker pour persister
les transitions `queued/running/failed/done/cancelled` au fil de l'exécution.
