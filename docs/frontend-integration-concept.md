# 🧩 Frontend & intégrations (concept actuel)

## Positionnement

L'UI Flask sert de cockpit opérationnel pour :

- gérer la bibliothèque source,
- lancer la chaîne archive → extraction → renommage → conversion,
- piloter les packets Audiobookshelf.

## Parcours utilisateur principal

1. Scanner la bibliothèque (`/api/library`)
2. Valider/extraire les archives
3. Renommer les dossiers à normaliser
4. Enqueue des jobs de conversion
5. Suivre progression et sorties `.m4b`
6. Préparer/soumettre packets Audiobookshelf

## UX déjà implémentée côté API

- Jobs + review bin
- Monitoring signatures (`/api/monitor`)
- Gestion outputs (liste, suppression, download, stream)
- Configuration exportable/importable

## Évolutions front ciblées

- meilleure visualisation des erreurs par job,
- filtres de queue et recherche,
- écran dédié marketplace plugins.
