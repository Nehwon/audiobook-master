# 🐳 Docker setup

## Lancement rapide

```bash
# Stack complète (tous les services)
docker compose up -d
```

## Services

Le `docker-compose.yml` du dépôt définit l'environnement applicatif (web + volumes de données) pour exécution locale.

- Image React par défaut : `ghcr.io/nehwon/audiobook-master-frontend:latest` (surcharge possible via `REACT_IMAGE`).

## Variables importantes

- `HOST` / `PORT` (runtime web)
- Variables `AUDIOBOOK_*` pour chemins runtime
- Variables `AUDIOBOOKSHELF_*` pour intégration distante

## Vérifications

```bash
docker compose ps
docker compose logs --tail=200
curl -fsS http://localhost:5000/health
```

## Volumes recommandés

- Source audio (lecture)
- Output `.m4b` (écriture)
- Logs
- Config web


## React + PostgreSQL

Pour préparer une base PostgreSQL et une interface React de développement :

- `postgres` et `react-ui` sont démarrés par défaut avec `docker compose up -d` via des images publiées (aucun build local requis).
- Configurez `AUDIOBOOK_DATABASE_URL` vers PostgreSQL, exemple :

```bash
AUDIOBOOK_DATABASE_URL=postgresql+psycopg://audiobook:audiobook123@postgres:5432/audiobook_manager
```

### Vérification des services

```bash
docker compose ps
curl -fsS http://localhost:8080/health
curl -fsS http://localhost:5173
```
