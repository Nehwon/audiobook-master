# Plan de phasage — UI v3 **from scratch**

## Décision non négociable
Nous repartons à zéro, sans patch de l’UI/architecture existante.

## Stack imposée
- **Backend**: FastAPI (REST + WebSockets)
- **Database**: PostgreSQL + `asyncpg` + triggers `LISTEN/NOTIFY`
- **Frontend**: React **ou** Svelte (choix en Phase 0), client WebSocket natif
- **UI kit / style**: Tailwind CSS **ou** CoreUI (choix en Phase 0)

---

## Architecture cible (V3)

```text
[Svelte + Tailwind/CoreUI]
          |
   (WebSocket + HTTP)
          |
 [FastAPI: REST + WS Gateway]
          |
 [PostgreSQL]
   |  triggers + pg_notify
   +-----------------------> [FastAPI Notifier -> Broadcast WS]
```

Principes:
1. Aucun couplage avec les templates Flask historiques.
2. Contrat d’événements versionné dès le départ.
3. Reconnexion WebSocket et idempotence backend obligatoires.

---

## Phase 0 — Kickoff produit & choix des variantes (3 jours)

### Objectifs
- Verrouiller les décisions techniques et UX de la v3.
- Définir un MVP clair (écrans + actions + métriques live).
- Geler les conventions de code pour éviter les réécritures.

### Technologies impliquées
- ADR techniques (Markdown)
- Maquettes (Figma ou schéma léger)
- RFC contrat d’événements JSON

### Décisions à prendre
- **Frontend**: React + Zustand/Redux Toolkit **ou** Svelte + stores.
- **Design system**: Tailwind **ou** CoreUI.
- **Auth**: JWT short-lived + refresh.

### Livrables
- ADR-001 architecture v3
- ADR-002 choix frontend/design system
- Backlog MVP (user stories + critères d’acceptation)

---

## Phase 1 — Bootstrap backend FastAPI (1 semaine)

### Objectifs
- Créer un backend v3 autonome et propre.
- Exposer un premier lot d’API REST pour entités cœur.
- Préparer l’intégration temps réel.

### Technologies impliquées
- FastAPI, Uvicorn
- Pydantic v2
- SQLAlchemy async + asyncpg
- Alembic
- Pytest

### Livrables
- Arborescence backend v3 (`app/api`, `app/services`, `app/db`)
- Endpoints: `/health`, `/api/v3/*`
- Schéma PostgreSQL initial + migrations Alembic
- Tests API de base (CRUD + erreurs)

---

## Phase 2 — Pipeline temps réel PostgreSQL -> WebSocket (1 semaine)

### Objectifs
- Mettre en place la propagation automatique des changements DB.
- Garantir une diffusion fiable et ordonnée des événements.

### Technologies impliquées
- Triggers PostgreSQL (`AFTER INSERT/UPDATE/DELETE`)
- `pg_notify(channel, payload)`
- `asyncpg` listener dans FastAPI
- ConnectionManager WebSocket (broadcast + heartbeat)

### Contrat d’événements (v1)
```json
{
  "schema_version": 1,
  "event_id": "uuid",
  "event_type": "insert|update|delete",
  "entity": "job|packet|...",
  "entity_id": "string",
  "timestamp": "ISO-8601",
  "payload": {}
}
```

### Livrables
- Migrations SQL trigger + function notify
- Service `PostgresNotifier`
- Endpoint WS `/ws`
- Tests d’intégration: write DB -> message WS reçu

---

## Phase 3 — Frontend v3 (MVP) (1 à 2 semaines)

### Objectifs
- Implémenter une UI dashboard moderne et lisible.
- Connecter l’UI aux API REST + WebSocket sans polling.

### Technologies impliquées
- React + Vite + React Query + Zustand/Redux Toolkit
  - **ou** Svelte + Vite + stores
- Tailwind CSS **ou** CoreUI
- Client WebSocket avec reconnexion exponentielle

### Écrans MVP
- Vue tableau de bord (KPI + statut connexion)
- Liste des jobs/packets (live updates)
- Détail d’un job + timeline d’événements
- Gestion erreurs/notifications utilisateur

### Livrables
- Application frontend v3 buildable en CI
- Composants UI réutilisables
- Gestion état global + cache serveur
- Tests UI unitaires (et premiers E2E)

---

## Phase 4 — Sécurité, observabilité, qualité (1 semaine)

### Objectifs
- Sécuriser API et WS avant ouverture large.
- Instrumenter la plateforme pour mesurer stabilité/perf.

### Technologies impliquées
- JWT + contrôle d’accès par scope
- CORS strict + rate limiting
- Logs structurés JSON
- Prometheus/Grafana (ou stack équivalente)
- Sentry frontend/backend

### Livrables
- Auth WS/REST en production mode
- Dashboards ops (latence API, connexions WS, erreurs JS)
- Budget perf (TTFB API, délai propagation event)

---

## Phase 5 — Préproduction & tests de charge (1 semaine)

### Objectifs
- Valider le comportement en conditions réalistes multi-clients.
- Détecter les goulots (DB, WS, sérialisation payload).

### Technologies impliquées
- k6/Locust (charge API + WS)
- Playwright (E2E parcours critiques)
- Jeux de données volumétriques PostgreSQL

### Livrables
- Rapport de charge (p50/p95/p99)
- Plan de tuning (indexes, pooling, taille payload)
- Go/No-Go documenté

---

## Phase 6 — Mise en production v3 (3 à 5 jours)

### Objectifs
- Déployer la v3 de manière contrôlée.
- Assurer rollback opérationnel en quelques minutes.

### Technologies impliquées
- Docker Compose / Kubernetes selon cible
- Reverse proxy (Traefik/Nginx)
- Feature flags runtime

### Livrables
- Déploiement progressif (interne -> pilote -> général)
- Runbook incident + rollback
- Checklist post-release (24h/72h)

---

## Planning recommandé (8 semaines)
- **S1**: Phase 0
- **S2**: Phase 1
- **S3**: Phase 2
- **S4-S5**: Phase 3
- **S6**: Phase 4
- **S7**: Phase 5
- **S8**: Phase 6

---

## KPI de réussite v3
- Temps moyen de propagation DB -> UI < **500 ms**
- Taux de reconnexion WS réussie > **99%**
- Erreurs frontend bloquantes < **0.5%** sessions
- Disponibilité API/WS > **99.9%**

Ce plan exécute strictement la direction demandée: **nouveau socle FastAPI + PostgreSQL async/trigger + frontend React/Svelte temps réel**.
