# Sprint 3 — API temps réel + contrat frontend

## Objectif

Terminer la couche API nécessaire à une UI réactive, sans polling agressif.

## Livrables implémentés

- Endpoints normalisés (`ok`, `data`, `meta`) pour la consultation frontend:
  - `GET /api/folders/errors`
  - `GET /api/folders/validations`
- Flux temps réel SSE:
  - `GET /api/events/stream`
  - Source prioritaire: `outbox_event` (PostgreSQL/SQLAlchemy)
  - Fallback: événements mémoire (`job_events`) si persistance indisponible
- Pagination / filtrage:
  - `offset` + `limit` sur erreurs/validations
  - filtres `folder_id`, `validation_key`
- Contrat frontend documenté:
  - `docs/api/openapi-frontend-sprint3.yaml`
- Tests de contrat API:
  - `tests/test_web_api_sprint3.py`

## Exemples rapides

### Erreurs d'un dossier

```bash
curl "http://localhost:5000/api/folders/errors?folder_id=Mon%20Dossier&limit=20&offset=0"
```

### Validations déjà calculées

```bash
curl "http://localhost:5000/api/folders/validations?folder_id=Mon%20Dossier&validation_key=archive.validate"
```

### Événements SSE

```bash
curl -N "http://localhost:5000/api/events/stream?since_id=0"
```

## Critères d'acceptation (Sprint 3)

- ✅ Le frontend peut se synchroniser via SSE (`/api/events/stream`).
- ✅ Les erreurs exploitables UI sont accessibles par dossier avec message utilisateur.
- ✅ Les validations déjà faites sont réutilisables via endpoint dédié.
- ✅ Contrat API minimal documenté + tests automatiques associés.
