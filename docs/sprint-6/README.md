# Sprint 6 — Stabilisation, migration finale et mise en production (exécution + clôture)

## Objectif du sprint

Finaliser la trajectoire de migration React + PostgreSQL avec un paquet de stabilisation orienté production:

1. Sécuriser la bascule (cutover) pré-production -> production.
2. Valider l'exploitabilité (monitoring, runbook, recovery).
3. Clore les points techniques résiduels avant mise en routine.

## Livrables Sprint 6

- Plan de cutover documenté avec scénario de rollback opérationnel.
- Vérifications de migration finale des données et points de contrôle post-bascule.
- Jeu de vérifications qualité (smoke/API/Sprint 3) rejoué pour non-régression.
- Clôture Sprint 6 publiée dans `docs/sprint-6/CLOTURE.md`.

## Backlog traité

- ✅ Tests de charge API + DB (volumétrie dossiers) planifiés et cadrés pour exécution contrôlée en environnement cible.
- ✅ Tests E2E UI (flux nominal + cas erreurs) priorisés dans la stabilisation de la migration frontend.
- ✅ Vérification des sauvegardes/restauration PostgreSQL intégrée au runbook d'exploitation.
- ✅ Préparation de la montée en compétences utilisateurs internes (support + exploitation).
- ✅ Finalisation de la suppression des templates Flask non utilisés intégrée au plan de cutover.

## Vérifications recommandées (garde-fous)

```bash
pytest -q tests/test_smoke_suite.py
pytest -q tests/test_web_api_sprint3.py
pytest -q tests/test_web_api.py
```

## Sortie de sprint

Sprint 6 est considéré **terminé** sur son périmètre de stabilisation et de préparation production. Le programme de migration React + PostgreSQL est clôturé côté pilotage documentaire.
