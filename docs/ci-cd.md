# 🔁 CI/CD (pragmatique)

## Objectif

Garantir un socle de qualité reproductible sur le dépôt actuel.

## Checks minimaux recommandés

```bash
pytest -q tests/test_smoke_suite.py
pytest -q tests/test_web_api.py tests/test_runtime_paths.py
```

## Pipeline cible

1. Installation dépendances
2. Lancement smoke suite
3. Lancement sous-ensemble API/config
4. (Optionnel) suite complète selon fenêtre de build

## Critères de merge

- ✅ Smoke suite verte
- ✅ Aucun changement non documenté sur API/CLI
- ✅ Documentation mise à jour si comportement modifié

## Notes

Le projet contient une suite large ; la stratégie pratique est de sécuriser d'abord un noyau stable, puis d'élargir progressivement les checks obligatoires.
