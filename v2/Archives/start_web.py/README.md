# Archive `start_web.py` (obsolète)

Ce dossier conserve **l'ancienne implémentation** de `start_web.py` pour référence historique.

## Pourquoi ce fichier est obsolète

L'ancienne version:
- manipulait `sys.path` pour viser un dossier `src/` historique,
- importait `web_ui` (chemin legacy non représentatif du module web actif),
- dupliquait un démarrage Flask déjà centralisé dans `web.app`.

La version active de `start_web.py` est désormais un wrapper de compatibilité qui délègue à `python -m web.app`.

## Contenu

- `start_web.py.obsolete`: snapshot de l'ancienne version conservée à titre documentaire.
