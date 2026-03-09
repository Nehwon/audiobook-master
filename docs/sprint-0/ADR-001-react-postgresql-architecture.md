# ADR-001 — Architecture cible React + PostgreSQL

- **Statut**: Accepted (validé pour lancement Sprint 1)
- **Date**: 2026-03-09
- **Contexte**: migration progressive de l'UI Flask actuelle vers React, avec persistance robuste des états de traitement et reprise automatique.

## Contexte

Le backend Flask gère déjà le pipeline de traitement et expose des routes API, mais:

- l'UI legacy est couplée au rendu serveur,
- l'état d'exécution n'est pas centralisé dans une base transactionnelle,
- la reprise après incident doit être systématisée.

Objectif: améliorer la fiabilité opérationnelle et l'expérience de suivi des traitements, avec bascule assumée vers la nouvelle architecture livrée par images Docker.

## Décision

### 1) Frontend

- Choisir **React + TypeScript** avec **Vite**.
- Utiliser **TanStack Query** pour la synchronisation serveur.
- Organiser l'application en modules métier: `folders`, `jobs`, `errors`, `validations`.

### 2) Temps réel

- Choisir **SSE (Server-Sent Events)** comme mécanisme principal:
  - simple à opérer avec HTTP,
  - compatible reverse proxy,
  - suffisant pour un flux unidirectionnel backend -> UI.
- Garder WebSocket en extension potentielle pour besoins futurs (bidirectionnel riche).

### 3) Persistance PostgreSQL

Modèle initial recommandé:

- `processing_job` (job global)
- `processing_step` (étapes d'un job)
- `folder_state` (vue état dossier)
- `validation_result` (résultat de validations réutilisables)
- `processing_error` (historique des erreurs)
- `outbox_event` (événements à diffuser vers SSE/monitoring)

### 4) Contrat d'erreur API unifié

Format standard JSON:

```json
{
  "code": "FOLDER_ARCHIVE_INVALID",
  "message": "L'archive est invalide ou incomplète.",
  "details": {
    "folder": "Author - Book"
  },
  "retryable": false
}
```

## Conséquences

### Positives

- État métier durable et requêtable.
- Reprise automatique possible de manière déterministe.
- UI plus réactive et découplée des templates legacy.

### Négatives / coûts

- Complexité d'exploitation supplémentaire (PostgreSQL + migrations + SSE).
- Effort de migration coordonnée backend/frontend sans phase de compatibilité legacy.

## Validation produit

Décisions explicitement validées:

- ADR-001 validé.
- Pas de préservation de compatibilité legacy (la publication par images Docker permet une bascule directe).
- Migration des données validée.
- Procédure de recovery validée.
- Passage en **Sprint 1** autorisé.

## Alternatives évaluées

1. **Rester 100% Flask templates**: faible coût initial, mais limite fortement la réactivité et la maintenabilité UI.
2. **WebSocket dès le départ**: plus puissant, mais complexité inutile pour le besoin actuel majoritairement push unidirectionnel.
3. **SQLite en transition**: facile localement, mais insuffisant pour concurrence/résilience cible.

## Risques et mitigations

- **Risque**: dérive de schéma DB.
  - **Mitigation**: migrations versionnées (Alembic), revues ADR, indexation explicite.
- **Risque**: duplication de traitement sur reprise.
  - **Mitigation**: idempotence métier + verrous logiques + heartbeat.
- **Risque**: contrat API instable.
  - **Mitigation**: tests de contrat JSON + versioning progressif des endpoints.
