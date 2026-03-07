# TODO technique

## Priorité P0 — Fiabilité immédiate

- [x] Corriger les régressions majeures de la suite `pytest -q`.
- [x] Identifier les tests devenus incompatibles avec l’implémentation courante et décider : corriger le code ou adapter le test.
- [x] Mettre en place une commande de validation minimale “toujours verte” (smoke suite).
- [x] Vérifier la cohérence des imports entre modules `core`, `web`, `integrations`.

## Priorité P1 — Robustesse produit

- [ ] Documenter précisément la matrice de formats audio réellement supportés (entrée/sortie + contraintes).
- [ ] Normaliser les messages d’erreur API (structure JSON uniforme).
- [ ] Renforcer la validation des chemins utilisateur (source/output/temp).
- [ ] Ajouter des tests d’intégration ciblés pour :
  - [ ] Upload Audiobookshelf (auth + upload + scan).
  - [ ] Pipeline archive → extraction → renommage → job enqueue.

## Priorité P2 — Maintenabilité

- [ ] Éliminer/archiver progressivement les scripts legacy non alignés (`run.py`, `start_web.py`) ou les remettre en cohérence.
- [ ] Factoriser la configuration partagée CLI/Web pour limiter la divergence des defaults.
- [ ] Réduire la dette documentaire en gardant le README concis et les détails dans `docs/`.

## Priorité P3 — Observabilité & DX

- [ ] Ajouter une commande de diagnostic unique (dépendances, ffmpeg, dossiers, variables env).
- [ ] Proposer un profil de logs “debug conversion” activable sans modifier le code.
- [ ] Améliorer la documentation développeur sur le cycle local (test, debug, release).
