# Plan de sprints détaillé — Migration UI React + PostgreSQL

## Objectifs globaux

1. **Passer l'UI en React** pour obtenir une interface réactive (mise à jour instantanée des traitements backend, états de dossiers, logs, erreurs).
2. **Passer sur PostgreSQL** pour persister les états d'exécution et de validation, reprendre automatiquement après incident/redémarrage, et afficher les erreurs de manière claire dans la zone **Dossiers**.

## Hypothèses et contraintes

- Backend Flask conservé comme socle d'API JSON stable, sans objectif de maintien d'une UI legacy en parallèle.
- Migration incrémentale pour éviter un « big bang » risqué.
- Les traitements existants (jobs/pipeline) restent la source métier, mais leur orchestration devient **pilotée par l'état en base**.
- Objectif de continuité: aucune perte d'information sur les traitements en cours pendant la migration.

---

## Sprint 0 — Cadrage technique et architecture (1 semaine)

> Statut: **terminé et validé**. Livrables approuvés, passage en Sprint 1 validé.

### But
Valider l'architecture cible et découper techniquement les migrations React + PostgreSQL.

### Livrables

- Dossier d'architecture (ADR) couvrant:
  - Frontend React (choix stack: Vite + React + TypeScript recommandé).
  - Mode de mise à jour temps réel (SSE recommandé, WebSocket en option).
  - Modèle de données PostgreSQL pour `jobs`, `folders`, `validation_states`, `processing_errors`, `events`.
- Cartographie des endpoints existants et nouveaux endpoints API.
- Plan de migration des données (fichiers/états existants vers PostgreSQL).
- Stratégie de reprise automatique au boot (recovery procedure).

### Backlog sprint

- [x] Atelier de modélisation des états de traitement (state machine explicite).
- [x] Définition d'un contrat d'erreur standard (`code`, `message`, `details`, `retryable`).
- [x] Définition du contrat d'événements UI temps réel (`job.updated`, `folder.failed`, etc.).
- [x] Définition des KPI de succès (temps de rafraîchissement UI, taux de reprise, taux d'erreurs muettes = 0).

### Critères d'acceptation

- Architecture validée par l'équipe.
- Risques principaux documentés avec plans de mitigation.

---

## Sprint 1 — Fondations PostgreSQL + persistance d'états (2 semaines)

> Statut: **autorisé à démarrer** (validation produit).

### But
Mettre en place PostgreSQL et enregistrer toutes les informations minimales nécessaires à la reprise.

### Livrables

- Connexion PostgreSQL intégrée à l'application.
- Migrations SQL versionnées (ex: Alembic).
- Tables initiales:
  - `processing_job`
  - `processing_step`
  - `folder_state`
  - `validation_result`
  - `processing_error`
  - `outbox_event` (pour diffusion UI/monitoring)
- Écriture transactionnelle des états clés pendant les traitements.

### Backlog sprint

- [x] Ajouter couche repository/service pour découpler la logique métier de la DB.
- [x] Persister transitions d'état (queued, running, failed, done, cancelled).
- [x] Persister erreurs techniques + fonctionnelles avec contexte (stacktrace optionnelle + message utilisateur).
- [x] Ajouter index sur colonnes de recherche (status, updated_at, folder_id).
- [x] Préparer scripts de bootstrap et migration des environnements (docker-compose inclus).

### Critères d'acceptation

- En cas de redémarrage, les jobs en cours sont visibles en base avec état cohérent.
- Les erreurs sont historisées et requêtables par dossier/job.

---

## Sprint 2 — Reprise automatique et résilience des traitements (2 semaines)

### But
Automatiser la reprise des traitements interrompus et sécuriser l'exécution.

### Livrables

- Mécanisme de recovery au démarrage:
  - Détection des jobs `running` orphelins.
  - Passage en `retry_pending` ou reprise directe selon politique.
- Politique de retry configurable (max tentatives, backoff).
- Verrous/logique d'idempotence pour éviter les doubles traitements.
- Journal d'audit des reprises automatiques.

### Backlog sprint

- [ ] Ajouter un `heartbeat` sur jobs en exécution.
- [ ] Définir timeout d'abandon d'un job sans heartbeat.
- [ ] Implémenter stratégie de reprise par type d'étape (safe retry / manual intervention).
- [ ] Exposer endpoint admin `/api/recovery/status`.
- [ ] Tests d'intégration crash/restart (killed worker puis relance).

### Critères d'acceptation

- Après crash simulé, reprise automatique sans action manuelle pour les cas nominalement retryables.
- Pas de duplication de sorties pour un même job (idempotence vérifiée).

---

## Sprint 3 — API temps réel + contrat frontend (1 à 2 semaines)

### But
Fournir une API robuste pour piloter une UI réactive.

### Livrables

- Endpoints REST normalisés pour dossiers, jobs, états, validations, erreurs.
- Flux temps réel (SSE) pour notifications de changement d'état.
- Pagination/filtrage côté API pour dossiers et historique erreurs.
- Documentation OpenAPI minimale pour les routes frontend.

### Backlog sprint

- [ ] Introduire schémas de réponse unifiés.
- [ ] Ajouter endpoint erreurs par dossier pour affichage ciblé en UI.
- [ ] Ajouter endpoint « validations déjà faites » pour éviter recalcul.
- [ ] Brancher l'outbox events vers SSE.
- [ ] Ajouter tests contrat API (snapshot JSON / tests schéma).

### Critères d'acceptation

- Le frontend peut se synchroniser sans polling agressif.
- Tous les cas d'erreurs affichables disposent d'un message utilisateur clair.

---

## Sprint 4 — Migration UI React (2 semaines)

### But
Remplacer l'UI actuelle par une UI React tout en conservant les capacités métiers existantes.

### Livrables

- Application React initiale (routing, layout, design system de base).
- Page principale « Dossiers » connectée à l'API.
- Store d'état client (TanStack Query recommandé + cache invalidation SSE).
- Composants de statut (badges, progression, erreurs).

### Backlog sprint

- [ ] Implémenter liste dossiers + détail d'un dossier.
- [ ] Implémenter rendu d'état en temps réel (running/progress/done/failed).
- [ ] Implémenter panneaux erreurs et validations.
- [ ] Ajouter UX de robustesse: skeletons, empty states, retry UI.
- [ ] Instrumentation frontend (logs erreurs UI + métriques de rafraîchissement).

### Critères d'acceptation

- L'UI affiche les changements backend en quelques secondes max.
- Les parcours principaux (lancer, suivre, consulter résultat/erreur) sont fonctionnels.

---

## Sprint 5 — Affichage rouge des erreurs dans « Dossiers » + validation persistée (1 semaine)

### But
Implémenter le besoin fonctionnel précis demandé pour les erreurs et la validation.

### Livrables

- Affichage rouge explicite des dossiers en erreur.
- Message d'erreur clair et actionnable dans la zone « Dossiers ».
- Réutilisation des validations déjà enregistrées (pas de recalcul inutile).
- Lien vers détail technique (option « voir plus »).

### Backlog sprint

- [ ] Ajouter mapping `error_code -> message utilisateur`.
- [ ] Créer composant `FolderErrorBanner` (couleurs, icône, texte).
- [ ] Ajouter tri/filtre « dossiers en erreur ».
- [ ] Ajouter indicateur « validation réutilisée ».
- [ ] Tests UI + accessibilité (contraste, lecteurs d'écran).

### Critères d'acceptation

- Un dossier en erreur est immédiatement identifiable visuellement.
- Le message affiché permet de comprendre quoi faire ensuite.
- Les validations persistées empêchent les retraitements inutiles.

---

## Sprint 6 — Stabilisation, migration finale et mise en production (1 à 2 semaines)

### But
Sécuriser la bascule finale et garantir l'exploitabilité en production.

### Livrables

- Plan de cutover (pré-prod -> prod) avec rollback.
- Migration de données finale exécutée et vérifiée.
- Tableaux de bord de monitoring (erreurs, retries, latence UI, backlog jobs).
- Documentation d'exploitation (runbook incidents + recovery manuel).

### Backlog sprint

- [ ] Tests de charge API + DB (volumétrie dossiers).
- [ ] Tests E2E UI (flux nominal + cas erreurs).
- [ ] Vérifier sauvegardes/restauration PostgreSQL.
- [ ] Former les utilisateurs internes sur la nouvelle UI.
- [ ] Finaliser la suppression des templates Flask non utilisés après cutover Docker.

### Critères d'acceptation

- Déploiement prod sans interruption majeure.
- Reprise incident documentée et testée.
- Objectifs de performance et fiabilité atteints.

---

## Récapitulatif planning (indicatif)

- Sprint 0: 1 sem.
- Sprint 1: 2 sem.
- Sprint 2: 2 sem.
- Sprint 3: 1–2 sem.
- Sprint 4: 2 sem.
- Sprint 5: 1 sem.
- Sprint 6: 1–2 sem.

**Total estimé: 10 à 12 semaines** (selon disponibilité équipe et dette technique découverte).

## Risques majeurs et mitigation

- **Risque:** Sous-estimation de la reprise automatique.  
  **Mitigation:** Prioriser Sprint 2 tôt, avec tests crash/restart automatisés.
- **Risque:** Régression métier lors de la migration UI.  
  **Mitigation:** API contract-first + E2E comparatifs old/new.
- **Risque:** Schéma de données trop rigide.  
  **Mitigation:** ADR de modélisation + migrations incrémentales.
- **Risque:** Messages d'erreurs insuffisamment clairs.  
  **Mitigation:** Taxonomie d'erreurs + revue UX dédiée Sprint 5.

## KPIs de succès

- Taux de reprise automatique réussie après crash > 95%.
- 0 perte d'état métier entre redémarrages.
- Temps de propagation backend -> UI < 3 s (p95).
- Réduction des revalidations inutiles > 80%.
- 100% des erreurs critiques visibles en UI avec message actionnable.
