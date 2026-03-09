# Sprint 0 — Kit de démarrage

Ce dossier lance le **Sprint 0 (cadrage technique et architecture)** de la migration React + PostgreSQL.

## Livrables inclus

1. **ADR architecture cible**
   - [`ADR-001-react-postgresql-architecture.md`](./ADR-001-react-postgresql-architecture.md)
2. **Cartographie API (existant + cible)**
   - [`api-mapping.md`](./api-mapping.md)
3. **Plan de migration des états vers PostgreSQL**
   - [`data-migration-plan.md`](./data-migration-plan.md)
4. **Procédure de reprise automatique au boot**
   - [`recovery-procedure.md`](./recovery-procedure.md)

## Décisions Sprint 0 (résumé)

- Frontend cible: **Vite + React + TypeScript**.
- Temps réel: **SSE** en standard, WebSocket optionnel plus tard.
- Persistance cible: PostgreSQL avec tables dédiées aux jobs, dossiers, validations, erreurs et événements.
- Contrat d'erreur unifié côté API: `code`, `message`, `details`, `retryable`.

## Definition of Done Sprint 0

- [x] Architecture cible documentée et argumentée.
- [x] Endpoints legacy inventoriés + endpoints cibles proposés.
- [x] Stratégie de migration des données décrite étape par étape.
- [x] Procédure de recovery au démarrage définie.
- [x] Risques principaux et mitigations explicités.
