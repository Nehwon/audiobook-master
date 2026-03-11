# 📌 Cartographie des Endpoints API

## 📡 Endpoints existants

| Méthode | Endpoint | Rôle |
|---|---|---|
| `GET` | `/` | UI principale |
| `GET` | `/api/library` | Inventaire source |
| `POST` | `/api/archive/validate` | Validation archive |
| `POST` | `/api/extract` | Extraction archive |
| `POST` | `/api/rename` | Renommage dossier |
| `POST` | `/api/jobs/enqueue` | Créer jobs conversion |
| `GET` | `/api/jobs` | Suivi jobs |
| `GET` | `/api/monitor` | Signatures d'état |
| `GET` | `/api/outputs` | Liste sorties `.m4b` |
| `GET` | `/api/download/<filename>` | Téléchargement sortie |
| `GET` | `/health` | Santé service |

## 📡 Nouveaux Endpoints API

| Méthode | Endpoint | Rôle |
|---|---|---|
| `GET` | `/api/folders` | Liste des dossiers avec états |
| `GET` | `/api/folders/<id>/errors` | Erreurs par dossier |
| `GET` | `/api/validations` | Validations déjà faites |
| `POST` | `/api/sse/subscribe` | Souscription SSE |
| `GET` | `/api/recovery/status` | État de la reprise automatique |

## 🔄 Migration des données

1. **Inventaire des données existantes** : Fichiers, dossiers, archives, états de traitement.
2. **Modélisation PostgreSQL** : Tables `library_item`, `processing_job`, `processing_step`, `folder_state`, `validation_result`, `processing_error`, `outbox_event`.
3. **Migration incrémentale** : Scripts de migration pour chaque table avec vérification de la cohérence des données.
4. **Vérification de la continuité** : Tests d'intégration pour s'assurer que les données migrées sont correctement récupérées et affichées.

## 🔄 Stratégie de reprise automatique

1. **Détection des jobs `running` orphelins** : Vérification des jobs en cours sans heartbeat.
2. **Passage en `retry_pending` ou reprise directe** : Selon la politique de retry.
3. **Politique de retry configurable** : Max tentatives, backoff.
4. **Verrous/logique d'idempotence** : Éviter les doubles traitements.
5. **Journal d'audit des reprises automatiques** : Historique des actions de reprise.

## 📝 Conclusion

La cartographie des endpoints et la stratégie de migration permettent de préparer une transition fluide vers une architecture React + PostgreSQL. Les prochaines étapes consistent à valider cette architecture et à commencer l'implémentation des nouvelles fonctionnalités.
