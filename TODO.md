# TODO produit & technique (pilotage par sprints)

## Sprint 1 — Socle d'exécution & visibilité (en cours)

### Objectifs
- [x] Préparer un plan de sprint exploitable depuis `TODO.md`.
- [x] Ajouter une commande de diagnostic CLI unique (dépendances, binaires, répertoires, variables d'environnement).
- [x] Ajouter un profil de logs `debug conversion` activable sans modifier le code.
- [x] Documenter la boucle locale de dev (test, debug, release) avec une checklist courte.

### Livrables attendus
- [x] Nouveau module de diagnostic CLI et option `--diagnostic`.
- [x] Documentation utilisateur enrichie avec exemples de diagnostics et dépannage.

## Sprint 2 — Frontend d'intégration Audiobookshelf

### Objectifs
- [x] Interface pour gérer les paquets d'upload (statut, progression, validation métadonnées).
- [x] Parcours de correction/enrichissement des métadonnées avant soumission.
- [x] Préparation d'un brouillon de changelog assisté IA (édition manuelle avant envoi).
- [x] Permettre la création d'un paquet à partir des fichiers `Output`.
- [x] Permettre le retrait d'un fichier d'un paquet avant soumission.

### Livrables attendus
- [x] Écran "paquets" avec actions de publication.
- [x] Workflow de prévisualisation de payload Audiobookshelf.

## Sprint 3 — Planification & diffusion

### Objectifs
- [ ] Programmer la publication différée des paquets (date/heure).
- [ ] Diffuser un message de changelog vers canaux configurés (phase 1: Discord, Telegram, WhatsApp, email).
- [ ] Ajouter une action de nettoyage manuel post-publication.

### Livrables attendus
- [ ] Scheduler fiable avec état de jobs.
- [ ] Connecteurs de diffusion initiale.

## Sprint 4 — Écosystème plugins

### Objectifs
- [ ] Mettre à niveau en priorité l'intégration/plugin Audiobookshelf.
- [ ] Concevoir un marketplace de plugins (découverte + installation).
- [ ] Définir un contrat de versionnement et de compatibilité des plugins.

### Livrables attendus
- [ ] Spécification de registre plugins.
- [ ] Prototype d'installation de plugin depuis source distante.

---

## Historique (déjà réalisé)

### Priorité P0 — Fiabilité immédiate
- [x] Corriger les régressions majeures de la suite `pytest -q`.
- [x] Identifier les tests devenus incompatibles avec l’implémentation courante et décider : corriger le code ou adapter le test.
- [x] Mettre en place une commande de validation minimale “toujours verte” (smoke suite).
- [x] Vérifier la cohérence des imports entre modules `core`, `web`, `integrations`.

### Priorité P1 — Robustesse produit
- [x] Documenter précisément la matrice de formats audio réellement supportés (entrée/sortie + contraintes).
- [x] Normaliser les messages d’erreur API (structure JSON uniforme).
- [x] Renforcer la validation des chemins utilisateur (source/output/temp).
- [x] Ajouter des tests d’intégration ciblés pour :
  - [x] Upload Audiobookshelf (auth + upload + scan).
  - [x] Pipeline archive → extraction → renommage → job enqueue.

### Priorité P2 — Maintenabilité
- [x] Éliminer/archiver progressivement les scripts legacy non alignés (`run.py`, `start_web.py`) ou les remettre en cohérence.
- [x] Factoriser la configuration partagée CLI/Web pour limiter la divergence des defaults.
- [x] Réduire la dette documentaire en gardant le README concis et les détails dans `docs/`.
- [x] Refactoriser la récupération de métadonnées externes en architecture de plugins (un plugin par source/site).
- [x] Refactoriser l'acquisition de covers en architecture de plugins (fournisseurs interchangeables).
