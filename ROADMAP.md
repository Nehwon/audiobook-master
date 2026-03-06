# Roadmap

Cette roadmap se concentre sur des objectifs vérifiables à partir du code présent dans le dépôt.

## Horizon court terme (0–1 mois)

- **Stabiliser la base de tests**
  - Réduire drastiquement le nombre d’échecs sur `pytest -q`.
  - Isoler les tests obsolètes ou non alignés avec l’implémentation actuelle.
  - Définir un “socle CI minimal” fiable (smoke tests obligatoires).

- **Clarifier les points d’entrée**
  - Conserver un chemin officiel pour la CLI (`core/main.py`).
  - Conserver un chemin officiel pour le web (`web/app.py`).
  - Documenter explicitement les scripts legacy et leur statut.

- **Durcir les flux archives/renommage**
  - Ajouter des validations supplémentaires sur les payloads API.
  - Renforcer les protections contre conflits et collisions de noms.

## Horizon moyen terme (1–3 mois)

- **Fiabiliser la conversion audio**
  - Uniformiser les stratégies de conversion et les retours d’erreur FFmpeg.
  - Consolider la gestion de chapitres et métadonnées dans le flux principal.

- **Améliorer l’observabilité**
  - Structurer davantage les logs (par job, niveau, composant).
  - Ajouter des indicateurs explicites dans `/api/monitor` utiles à l’exploitation.

- **Rationaliser la configuration**
  - Éviter les valeurs par défaut trop spécifiques machine.
  - Introduire une hiérarchie claire des sources de configuration (env > fichier > défaut).

## Horizon long terme (3+ mois)

- **Convergence architecture**
  - Réduire les duplications entre composants historiques et actuels.
  - Encapsuler les intégrations externes (Ollama, Audiobookshelf) derrière des interfaces stables.

- **Qualité de release**
  - Définir des critères de release mesurables (tests passants, checks lint, smoke Docker).
  - Mettre en place une stratégie de version/release disciplinée (notes courtes, diff clair).

## Hors périmètre immédiat

- Réécriture complète de l’UI.
- Migration vers un autre framework web.
- Refonte massive du packaging tant que la base de tests n’est pas stabilisée.
