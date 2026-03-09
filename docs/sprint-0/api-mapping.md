# Sprint 0 — Cartographie API (existant -> cible)

## Endpoints existants (base actuelle)

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/library` | Inventaire source |
| POST | `/api/archive/validate` | Validation archive |
| POST | `/api/extract` | Extraction archive |
| POST | `/api/rename` | Renommage dossier |
| POST | `/api/jobs/enqueue` | Création de jobs |
| GET | `/api/jobs` | Suivi des jobs |
| GET | `/api/monitor` | Signatures état global |
| GET | `/api/outputs` | Liste sorties |
| GET | `/api/download/<filename>` | Téléchargement |

## Endpoints cibles (contrat React/PostgreSQL)

### Dossiers

- `GET /api/folders?status=&q=&page=`
- `GET /api/folders/{folder_id}`
- `GET /api/folders/{folder_id}/errors`
- `GET /api/folders/{folder_id}/validations`

### Jobs

- `POST /api/jobs` (enqueue normalisé)
- `GET /api/jobs?status=&folder_id=&page=`
- `GET /api/jobs/{job_id}`
- `POST /api/jobs/{job_id}/cancel`

### Recovery / admin

- `GET /api/recovery/status`
- `POST /api/recovery/reconcile`

### Temps réel

- `GET /api/events/stream` (SSE)

Événements initiaux proposés:
- `job.created`
- `job.updated`
- `job.failed`
- `folder.updated`
- `folder.failed`
- `validation.completed`

## Contrats de réponse normalisés

### Réponse succès

```json
{
  "data": {},
  "meta": {
    "request_id": "req_xxx"
  }
}
```

### Réponse erreur

```json
{
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "Job introuvable",
    "details": {
      "job_id": "..."
    },
    "retryable": false
  }
}
```

## Plan de transition API

1. Préserver endpoints legacy pour compatibilité.
2. Introduire endpoints cibles sous les mêmes préfixes `/api/...` avec réponses normalisées.
3. Basculer UI React vers les nouveaux endpoints.
4. Déprécier progressivement les routes legacy non utilisées.
