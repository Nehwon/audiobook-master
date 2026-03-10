# 🐳 Docker setup

## Lancement rapide

```bash
# Stack backend seule
docker compose up -d

# Stack avec PostgreSQL + UI React (profilée)
docker compose --profile database --profile frontend up -d --build
```

## Services

Le `docker-compose.yml` du dépôt définit l'environnement applicatif (web + volumes de données) pour exécution locale.

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

- Activez le profil `database` pour démarrer `postgres`.
- Activez le profil `frontend` pour démarrer `react-ui` (Vite sur le port `5173`).
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
