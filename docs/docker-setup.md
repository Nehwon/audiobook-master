# 🐳 Docker setup

## Lancement rapide

```bash
docker compose up -d
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
