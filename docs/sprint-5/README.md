# Sprint 5 — Erreurs rouges dans « Dossiers » + validation persistée (documentation finalisée)

## Objectif du sprint

Transformer le cadrage Sprint 4 en plan d'implémentation exécutable pour l'expérience utilisateur du parcours « Dossiers », avec deux priorités:

1. Rendre les dossiers en échec immédiatement visibles (signal rouge explicite).
2. Réutiliser les validations déjà persistées pour éviter les retraitements inutiles.

> Ce sprint est documenté ici comme un **sprint de finalisation fonctionnelle et UX prêt à implémenter**.

## Livrables documentaires produits/utilisés

- `docs/frontend-integration-concept.md` — articulation API/SSE/UI exploitée pour le parcours « Dossiers ».
- `docs/ui-migration-strategy.md` — stratégie d'intégration incrémentale conservée.
- `docs/ui-redesign-proposal.md` — conventions visuelles réutilisées pour statut/erreur.
- `docs/api/openapi-frontend-sprint3.yaml` — base contractuelle API exploitée pour états/erreurs/validations.
- `docs/SPRINTS_REACT_POSTGRESQL.md` — plan macro mis à jour avec Sprint 5 clôturé.

## Périmètre validé Sprint 5

- Mapping fonctionnel `error_code -> message utilisateur` défini au niveau produit.
- Composant cible `FolderErrorBanner` spécifié (couleur rouge, icône, message principal, action secondaire).
- Tri/filtre « dossiers en erreur » cadré dans le flux de navigation principal.
- Indicateur « validation réutilisée » défini dans le rendu d'état dossier.
- Exigences d'accessibilité explicitées (contraste, vocalisation du statut, actions clavier).

## Critères d'acceptation (documentaires)

- ✅ Un dossier en erreur est identifiable en un coup d'œil.
- ✅ Le message utilisateur d'erreur est compréhensible et actionnable.
- ✅ La réutilisation d'une validation persistée est visible côté interface.
- ✅ Le backlog d'implémentation est prêt pour exécution Sprint 6 sans ambiguïté.

## Vérifications recommandées

```bash
pytest -q tests/test_smoke_suite.py
pytest -q tests/test_web_api_sprint3.py
```

## Sortie de sprint

Sprint 5 est considéré **terminé côté documentation**. Les éléments UI/API sont suffisamment précisés pour implémentation et stabilisation en sprint suivant.
