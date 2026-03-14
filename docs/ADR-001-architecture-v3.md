# ADR-001: Architecture v3 - FastAPI + PostgreSQL + WebSocket

**Status**: Accepted  
**Date**: 2026-03-14  
**Decision**: Adopter une architecture moderne avec FastAPI, PostgreSQL async et WebSocket temps réel  

---

## Contexte

L'architecture actuelle basée sur Flask présente des limitations pour le développement futur :
- Templates legacy difficiles à maintenir
- Pas de support natif WebSocket
- Persistance limitée à SQLite
- Difficultés pour le temps réel et la scalabilité

## Decision

Nous adoptons une architecture entièrement nouvelle basée sur :
- **Backend**: FastAPI (REST + WebSockets)
- **Database**: PostgreSQL + `asyncpg` + triggers `LISTEN/NOTIFY`
- **Frontend**: React ou Svelte (choix en Phase 0)
- **UI kit**: Tailwind CSS ou CoreUI (choix en Phase 0)

## Architecture Cible

```text
[React/Svelte + Tailwind/CoreUI]
          |
   (WebSocket + HTTP)
          |
[FastAPI: REST + WS Gateway]
          |
[PostgreSQL]
   |  triggers + pg_notify
   +-----------------------> [FastAPI Notifier -> Broadcast WS]
```

## Principes Fondamentaux

1. **Aucun couplage avec les templates Flask historiques**
   - Clean break avec l'existant
   - Nouvelle base technique solide

2. **Contrat d'événements versionné dès le départ**
   - Schema versionné pour compatibilité
   - Évolution contrôlée des events

3. **Reconnexion WebSocket et idempotence backend obligatoires**
   - Robustesse temps réel
   - Gestion des déconnexions clientes

## Conséquences

### Positives
- ✅ Performance améliorée avec FastAPI
- ✅ Support natif WebSocket
- ✅ Scalabilité PostgreSQL
- ✅ Architecture moderne maintenable

### Négatives
- ❌ Réécriture complète du backend
- ❌ Courbe d'apprentissage équipe
- ❌ Migration des données existantes

## Implémentation

### Phase 1: Backend FastAPI
- Créer structure `app/api`, `app/services`, `app/db`
- Endpoints `/health`, `/api/v3/*`
- Schéma PostgreSQL initial

### Phase 2: Pipeline temps réel
- Triggers PostgreSQL `AFTER INSERT/UPDATE/DELETE`
- Service `PostgresNotifier`
- Endpoint WebSocket `/ws`

### Phase 3: Frontend v3
- Application React/Svelte moderne
- Connexion API REST + WebSocket
- Composants réutilisables

## Alternatives Considérées

1. **Améliorer Flask existant**
   - Rejeté: Complexité technique et limites WebSocket

2. **Adopter NestJS (Node.js)**
   - Rejeté: Changement de stack technologique trop important

3. **Microservices avec Go**
   - Rejeté: Trop complexe pour équipe actuelle

## Validation

Cette décision a été validée par :
- [ ] Lead Technique: __________________
- [ ] Lead Produit: __________________
- [ ] Architecture: __________________

---

**Statut**: ✅ **ACCEPTÉ** - Base technique pour UI v3
