# Sprint 0 — Plan de migration des données vers PostgreSQL

## Objectif

Migrer l'état opérationnel existant (jobs/folders/validations/erreurs) vers PostgreSQL **sans perte de continuité**.

## Sources actuelles à inventorier

- États de jobs en mémoire/processus.
- Signatures de monitoring (`/api/monitor`).
- Fichiers de sortie et conventions de nommage existantes.
- Données de validation éventuellement déduites des artefacts générés.

## Cible de persistance

- `processing_job`
- `processing_step`
- `folder_state`
- `validation_result`
- `processing_error`
- `outbox_event`

## Stratégie de migration incrémentale

1. **Phase A — Dual-write préparatoire**
   - Écrire les nouveaux états critiques en PostgreSQL en plus du comportement existant.
   - Garder l'UI legacy inchangée.

2. **Phase B — Backfill historique**
   - Script de backfill pour injecter l'historique minimal nécessaire:
     - dossiers connus,
     - derniers statuts jobs,
     - erreurs récentes exploitables.

3. **Phase C — Lecture prioritaire DB**
   - Faire lire `/api/jobs`, `/api/folders`, `/api/monitor` depuis PostgreSQL.
   - Conserver fallback legacy temporaire derrière feature flag.

4. **Phase D — Nettoyage**
   - Supprimer les chemins legacy d'état quand la stabilité est confirmée.

## Règles de cohérence

- Toute transition de statut job doit être transactionnelle.
- Toute erreur fonctionnelle/technique doit être persistée avec horodatage.
- L'état dossier doit être dérivable de la dernière vision cohérente des jobs/validations/erreurs.

## Validation de migration

- Vérifier qu'un redémarrage n'efface pas les jobs en cours.
- Vérifier que les dossiers en erreur restent visibles après restart.
- Vérifier que les validations déjà faites sont réutilisées sans retraitement inutile.
