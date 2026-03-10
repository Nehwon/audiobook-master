# Sprint 4 — Migration UI React (documentation de cadrage finalisée)

## Objectif du sprint

Préparer et verrouiller la migration UI React de façon exploitable pour l'implémentation, en s'appuyant sur les capacités backend déjà disponibles (API REST + SSE + persistance).

> Ce sprint est traité ici comme un **sprint documentaire de finalisation de conception**: il clôture le cadrage opérationnel avant développement frontend.

## Livrables documentaires produits/utilisés

- `docs/frontend-integration-concept.md` — intégration frontend/backend (flux, états, contrats).
- `docs/ui-migration-strategy.md` — stratégie de migration incrémentale UI.
- `docs/ui-redesign-proposal.md` — proposition d'UX et d'organisation écran.
- `docs/api/openapi-frontend-sprint3.yaml` — base de contrat API disponible pour l'écran Dossiers.
- `docs/SPRINTS_REACT_POSTGRESQL.md` — plan macro mis à jour avec statut Sprint 4 clôturé.

## Périmètre validé Sprint 4

- Architecture cible UI React confirmée (migration incrémentale, sans big-bang).
- Parcours prioritaire « Dossiers » cadré (lecture états/erreurs/validations).
- Stratégie de rafraîchissement temps réel validée via SSE.
- Exigences UX de robustesse documentées (empty states, retry, feedback visuel).
- Séquencement vers Sprint 5 clarifié (focus erreurs rouges + validation persistée côté UX).

## Critères d'acceptation (documentaires)

- ✅ Les artefacts de migration UI sont centralisés et cohérents.
- ✅ Le couplage API backend ↔ UI React est explicite et actionnable.
- ✅ Les dépendances inter-sprints sont identifiées avant implémentation.
- ✅ La préparation Sprint 5 est prête sans ambiguïté de périmètre.

## Vérifications recommandées

```bash
pytest -q tests/test_smoke_suite.py
pytest -q tests/test_web_api_sprint3.py
```

## Sortie de sprint

Sprint 4 est considéré **terminé côté documentation**. Le développement React peut démarrer sur la base de ce cadre validé.
