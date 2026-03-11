# ✅ TODO — UI v3 from scratch (plan atomique)

> Référence d’architecture : `FastAPI (API/WebSockets) + PostgreSQL (asyncpg + triggers) + React/Svelte + Tailwind/CoreUI + WebSocket client`.

## Phase 0 — Cadrage produit et standards

- [ ] Valider formellement la stack cible (backend, frontend, design system, auth).
- [ ] Définir le périmètre MVP (écrans, actions, flux critiques).
- [ ] Écrire l’ADR architecture v3 (principes, conventions, exclusions du legacy).
- [ ] Écrire le contrat d’événements temps réel v1 (schéma JSON versionné).
- [ ] Définir la stratégie de qualité (tests, observabilité, critères Go/No-Go).

## Phase 1 — Bootstrap backend FastAPI

- [ ] Créer l’arborescence backend v3 isolée (`app/api`, `app/services`, `app/db`).
- [ ] Mettre en place la configuration centralisée (env, settings, secrets).
- [ ] Initialiser PostgreSQL async (`SQLAlchemy async` + `asyncpg`).
- [ ] Créer les endpoints de base (`/health`, `/api/v3/*`).
- [ ] Mettre en place Alembic et la première migration de schéma.
- [ ] Ajouter les tests API CRUD fondamentaux.

## Phase 2 — Pipeline PostgreSQL -> WebSocket

- [ ] Implémenter les triggers `INSERT/UPDATE/DELETE` avec `pg_notify`.
- [ ] Créer le listener `asyncpg` côté FastAPI.
- [ ] Implémenter `ConnectionManager` WebSocket (connexion, déconnexion, broadcast).
- [ ] Ajouter heartbeat + gestion reconnexion côté serveur.
- [ ] Brancher la transformation DB event -> contrat événement v1.
- [ ] Écrire les tests d’intégration DB -> WS.

## Phase 3 — Frontend v3 (React ou Svelte)

- [ ] Initialiser l’application frontend v3 (Vite, structure modulaire).
- [ ] Intégrer le design system choisi (Tailwind ou CoreUI).
- [ ] Implémenter le client WebSocket (connexion, retry exponentiel, reprise).
- [ ] Connecter les appels REST (`GET/POST/PUT/DELETE`) et le cache applicatif.
- [ ] Construire les écrans MVP (dashboard, liste, détail, erreurs).
- [ ] Ajouter les tests unitaires UI des composants critiques.

## Phase 4 — Sécurité et observabilité

- [ ] Mettre en place l’authentification JWT pour REST et WebSocket.
- [ ] Appliquer CORS strict + rate limiting.
- [ ] Structurer les logs backend/frontend en JSON corrélable.
- [ ] Exposer les métriques techniques (API, WS, DB).
- [ ] Activer le suivi d’erreurs frontend/backend (Sentry ou équivalent).
- [ ] Définir et publier les SLO/SLA opérationnels.

## Phase 5 — Validation système et robustesse

- [ ] Écrire les scénarios E2E critiques (Playwright).
- [ ] Exécuter les tests de charge API + WebSocket (k6/Locust).
- [ ] Valider les scénarios de panne (DB indisponible, coupure réseau, backlog).
- [ ] Ajuster indexes/pooling/taille payload selon résultats.
- [ ] Formaliser le rapport Go/No-Go de validation.

## Phase 6 — Mise en production v3

- [ ] Préparer les manifests de déploiement (Docker/infra cible).
- [ ] Mettre en place le reverse proxy et le routage de la v3.
- [ ] Définir la stratégie de déploiement progressif (interne, pilote, général).
- [ ] Documenter le runbook incident et rollback.
- [ ] Exécuter la checklist post-release et valider les KPI de réussite.

## Règles d’exécution (non négociables)

- [ ] Aucun couplage fonctionnel avec les templates Flask legacy.
- [ ] Toute évolution temps réel doit respecter le contrat d’événements versionné.
- [ ] Toute fonctionnalité livrée doit avoir au minimum un test automatisé associé.
- [ ] Toute régression critique bloque la phase suivante tant qu’elle n’est pas corrigée.
