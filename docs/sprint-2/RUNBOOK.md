# Runbook Sprint 2 — Reprise manuelle minimale

## Objectif

Fournir la procédure d'exploitation minimale après incident lorsque la reprise automatique ne suffit pas.

## Pré-requis

- Accès à l'API admin (`/api/recovery/status`).
- Accès aux logs applicatifs (`web_debug.log` et logs processor).
- Accès SQL en lecture/écriture sur la base applicative.

## Procédure

1. **Diagnostiquer l'état global**
   - Appeler `GET /api/recovery/status`.
   - Vérifier les compteurs `manual_intervention` et `retry_pending`.

2. **Identifier les jobs bloqués**
   - Rechercher les jobs en `failed` avec `recovery_status=manual_intervention`.
   - Consulter `recovery_audit` pour la raison (`max_retries_exceeded`, etc.).

3. **Décider de l'action**
   - Si la cause est transitoire: remettre le job en file via l'UI/API de reprocess.
   - Si la cause est métier: corriger la donnée source puis reprocess.
   - Si la sortie existe déjà: ne pas relancer (idempotence), marquer comme traité.

4. **Relancer proprement**
   - Un seul job actif par dossier logique (clé d'idempotence).
   - Vérifier qu'aucun lock idempotent ne bloque le dossier avant relance.

5. **Valider la reprise**
   - Contrôler la transition vers `running` puis `done`.
   - Confirmer l'absence de doublon de sortie `.m4b`.

## Requêtes SQL utiles

```sql
-- Jobs nécessitant intervention
SELECT id, folder_id, status, recovery_status, retry_count, updated_at
FROM processing_job
WHERE recovery_status = 'manual_intervention'
ORDER BY updated_at DESC;

-- Décisions de recovery les plus récentes
SELECT job_id, decision, reason, created_at
FROM recovery_audit
ORDER BY created_at DESC
LIMIT 100;
```

## Critères de sortie incident

- Plus aucun job `manual_intervention` non traité.
- Tous les dossiers relancés atteignent `done` ou un état explicite documenté.
- Aucun doublon de sortie constaté.
