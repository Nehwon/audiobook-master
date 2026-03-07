# Concept — Frontend web pour l’intégration Audiobookshelf

## Objectif

Démarrer la conception d’un frontend web orienté **pilotage des paquets de publication** vers Audiobookshelf, avec un flux clair:

1. préparation d’un paquet,
2. enrichissement et validation des métadonnées,
3. soumission immédiate ou programmée,
4. suivi de progression,
5. nettoyage manuel post-publication.

---

## Périmètre Phase 1 (MVP)

### 1) Vue « Paquets d’upload »

- Liste des paquets détectés (statut, taille, nombre de fichiers, date de création).
- Filtres: `en attente`, `en préparation`, `prêt`, `planifié`, `publié`, `erreur`.
- Actions rapides:
  - ouvrir le détail,
  - lancer l’analyse des métadonnées,
  - planifier,
  - soumettre immédiatement,
  - nettoyer (manuel uniquement).

### 2) Détail d’un paquet

- Édition des champs clés:
  - titre, auteur(s), série, volume, narrateur, langue, tags,
  - description/synopsis,
  - couverture (actuelle + proposée).
- Bloc « suggestions externes »:
  - recherche Babelio / Google Books / Audible,
  - pré-remplissage des champs manquants en priorité,
  - comparaison « valeur actuelle » vs « valeur proposée ».
- Bloc « IA synopsis » (Ollama):
  - bouton de génération d’une version concise,
  - validation manuelle obligatoire avant remplacement.

### 3) Soumission Audiobookshelf

- Construction d’un payload visualisable avant envoi.
- Validation pré-envoi (champs obligatoires, connectivité, token).
- Envoi + affichage de progression par étape:
  - préparation,
  - upload,
  - scan bibliothèque,
  - confirmation finale.

### 4) Changelog multi-canaux

- Génération assistée (Ollama) d’un message de publication.
- Édition manuelle.
- Les canaux de diffusion sont gérés comme des **plugins de notification** (pas de liste hardcodée côté frontend).
- Cibles MVP attendues via plugins:
  - Discord,
  - Telegram,
  - WhatsApp,
  - Email.

### 5) Planification

- Date/heure de publication.
- Sélection des canaux de notification.
- Exécution asynchrone à échéance, avec traçabilité des statuts.

---

## Parcours utilisateur cible

1. L’utilisateur ouvre « Paquets d’upload ».
2. Il sélectionne un paquet en attente.
3. Le système analyse les métadonnées et propose des enrichissements.
4. L’utilisateur valide/édite les données et la couverture.
5. Il prépare le message de changelog.
6. Il choisit « Publier maintenant » ou « Programmer ».
7. Il suit la progression depuis la vue de statut.
8. Une fois publié, il peut cliquer sur « Nettoyer » (action explicite, non automatique).

---

## Proposition UX (structure d’écrans)

- `/integrations/audiobookshelf/packets`
  - tableau des paquets + actions.
- `/integrations/audiobookshelf/packets/:id`
  - onglets: `Métadonnées`, `Couverture`, `Synopsis`, `Soumission`, `Historique`.
- `/integrations/audiobookshelf/schedule`
  - planning des publications futures.
- `/integrations/audiobookshelf/settings`
  - paramètres API + gestion des plugins de notification (activation/configuration par canal).

---

## Contrats backend à prévoir

### Endpoints (proposition)

- `GET /api/integrations/audiobookshelf/packets`
- `GET /api/integrations/audiobookshelf/packets/{id}`
- `POST /api/integrations/audiobookshelf/packets/{id}/analyze`
- `POST /api/integrations/audiobookshelf/packets/{id}/metadata/suggest`
- `PUT /api/integrations/audiobookshelf/packets/{id}/metadata`
- `POST /api/integrations/audiobookshelf/packets/{id}/cover/suggest`
- `POST /api/integrations/audiobookshelf/packets/{id}/synopsis/summarize`
- `POST /api/integrations/audiobookshelf/packets/{id}/submit`
- `POST /api/integrations/audiobookshelf/packets/{id}/schedule`
- `POST /api/integrations/audiobookshelf/packets/{id}/cleanup`
- `GET /api/notifications/plugins`
- `PUT /api/notifications/plugins/{plugin_id}`

### Plugins de canaux (changelog)

- Le frontend récupère dynamiquement les canaux disponibles depuis un registre de plugins.
- Chaque plugin expose au minimum:
  - `id`, `name`, `enabled`,
  - schéma de configuration (ex: webhook, token, destinataires),
  - statut de validation (`ok`, `invalid`, `missing_secrets`).
- Lors d’une soumission/schedule, l’UI envoie la liste des `plugin_id` sélectionnés plutôt qu’un enum figé.
- Un échec d’un plugin ne doit pas invalider automatiquement la publication Audiobookshelf:
  - résultat détaillé par canal dans l’historique,
  - stratégie de retry configurable en phase 2.

### État de progression

- Utiliser un modèle de job unique (`queued`, `running`, `done`, `failed`) + sous-étapes métier.
- Prévoir un flux live (polling court en MVP, WebSocket en phase 2).

---

## Sécurité et garde-fous

- Confirmation explicite avant publication.
- Confirmation explicite avant nettoyage destructif.
- Journal d’audit minimal:
  - qui a soumis,
  - quand,
  - vers quelle cible,
  - résultat.
- Masquage des secrets dans l’UI et les logs.

---

## Plan d’implémentation proposé

### Sprint A — Cadrage & socle UI

- Créer la navigation `Integrations > Audiobookshelf`.
- Implémenter la liste des paquets + statuts mockés.
- Poser les contrats d’API côté backend (même si partiellement stub).

### Sprint B — Détail paquet & enrichissement

- Édition métadonnées.
- Suggestions externes + logique de fusion priorisant les champs manquants.
- Suggestion de synopsis via Ollama.

### Sprint C — Soumission, planification, notifications

- Soumission immédiate avec progression.
- Planification (job différé).
- Génération/édition du changelog et dispatch multi-canaux.

### Sprint D — Stabilisation

- Gestion d’erreurs fine.
- Journal d’audit.
- Tests E2E ciblés sur parcours critique.

---

## Critères d’acceptation MVP

- Un paquet peut être ouvert, édité et soumis avec retour de statut fiable.
- La planification fonctionne à date/heure choisies.
- Le changelog peut être généré, modifié, puis envoyé sur au moins un canal.
- Le nettoyage reste manuel et nécessite une confirmation.
