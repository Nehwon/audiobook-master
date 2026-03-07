# TODO technique

## Priorité P0 — Fiabilité immédiate

- [x] Corriger les régressions majeures de la suite `pytest -q`.
- [x] Identifier les tests devenus incompatibles avec l’implémentation courante et décider : corriger le code ou adapter le test.
- [x] Mettre en place une commande de validation minimale “toujours verte” (smoke suite).
- [x] Vérifier la cohérence des imports entre modules `core`, `web`, `integrations`.

## Priorité P1 — Robustesse produit

- [x] Documenter précisément la matrice de formats audio réellement supportés (entrée/sortie + contraintes).
- [x] Normaliser les messages d’erreur API (structure JSON uniforme).
- [x] Renforcer la validation des chemins utilisateur (source/output/temp).
- [x] Ajouter des tests d’intégration ciblés pour :
  - [x] Upload Audiobookshelf (auth + upload + scan).
  - [x] Pipeline archive → extraction → renommage → job enqueue.

## Priorité P2 — Maintenabilité

- [x] Éliminer/archiver progressivement les scripts legacy non alignés (`run.py`, `start_web.py`) ou les remettre en cohérence.
- [x] Factoriser la configuration partagée CLI/Web pour limiter la divergence des defaults.
- [x] Réduire la dette documentaire en gardant le README concis et les détails dans `docs/`.
- [ ] Refactoriser la récupération de métadonnées externes en architecture de plugins (un plugin par source/site).
- [ ] Refactoriser l'acquisition de covers en architecture de plugins (fournisseurs interchangeables).

## Priorité P3 — Observabilité & DX

- [ ] Ajouter une commande de diagnostic unique (dépendances, ffmpeg, dossiers, variables env).
- [ ] Proposer un profil de logs “debug conversion” activable sans modifier le code.
- [ ] Améliorer la documentation développeur sur le cycle local (test, debug, release).

# TODO Features

- [ ] Developper un frontend web pour la partie integration avec Audiobookshelf
    - [ ] Interface pour gérer les packets d'upload, leur statut et leur progression
          - Principe : Permettre à l'utilisateur de choisir un groupe de fichiers en attente pour les publier sur Audiobookshelf
          - Logique : Lors de la publication du packet, une lecture des métadonnées est effectuée. Celle-ci sont présenté à l'utilisateur pour qu'il les modifie, fasse un recherche sur un site externe (Ex: Babelio, Google books, ...). Les données récupérées sont ensuite proposées pour remplacer les données existantes en commençant par le manquantes. Une couverture est rechercher pour remplacer l'embeded si besoin. Les synopsis sont proposés à l'ollama pour un synthèse plus concise.
          - Une soumission est ensuite composée pour être présenté à l'API Audiobookshelf,
          - Lorsque le packet est complet, un bouton propose de le soumettre,
          - Dans le même temps, une demande de composition d'un message du type "Changelog" est demandée à l'ollama, l'utilisateur peut le modifier avant de le soumettre, et choisir le vecteur de soumission. Pour la phase 1 de développement, nous ciblerons discord, Telegram, whatsapp et email.
    - [ ] Interface pour programmer la publication effective vers audiobookshelf
          - Principe : Permettre à l'utilisateur de programmer la publication effective vers audiobookshelf
          - Logique : L'utilisateur peut choisir une date et une heure pour la publication effective vers audiobookshelf
