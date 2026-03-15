# Archive `run.py` (obsolète)

Ce dossier conserve **l'ancienne implémentation** de `run.py` pour référence historique.

## Pourquoi ce fichier est obsolète

L'ancienne version:
- manipulait `sys.path` pour viser un dossier `src/` historique,
- importait des modules non alignés avec l'architecture active,
- dupliquait la logique d'entrée CLI qui existe déjà dans `core.main`.

La version active de `run.py` est désormais un wrapper de compatibilité qui délègue à `python -m core.main`.

## Contenu

- `run.py.obsolete`: snapshot de l'ancienne version conservée à titre documentaire.
