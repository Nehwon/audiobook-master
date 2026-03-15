# 📌 Plan de Migration des Données

## 📡 Objectifs

1. **Persister toutes les informations nécessaires** : Fichiers, dossiers, archives, états de traitement.
2. **Normaliser le cycle de vie** : Utiliser un statut métier unique pour tous les objets.
3. **Conserver l'historique des transitions d'état** : Audit et observabilité.
4. **Centraliser les paramètres globaux** : Configuration dans `app_configuration`.
5. **Donner aux plugins leur propre système de configuration** : Tables spécialisées pour chaque type de plugin.

## 📡 Modèle de Données PostgreSQL

```mermaid

  1 | erDiagram
  2 |     LIBRARY_ITEM ||--o{ LIBRARY_ITEM_STATUS_HISTORY : "changes"
  3 |     LIBRARY_ITEM ||--o{ PROCESSING_JOB : "processed_by"
  4 |     APP_CONFIGURATION ||--o{ APP_CONFIGURATION_HISTORY : "versioned_by"
  5 |     LIBRARY_ITEM ||--o{ LIBRARY_ITEM : "parent_of"
  6 | 
  7 |     PLUGIN_REGISTRY ||--o{ PLUGIN_INSTANCE : "contains"
  8 |     PLUGIN_INSTANCE ||--|| PLUGIN_DISCORD_CONFIG : "typed_config"
  9 |     PLUGIN_INSTANCE ||--|| PLUGIN_TELEGRAM_CONFIG : "typed_config"
 10 |     PLUGIN_INSTANCE ||--|| PLUGIN_EMAIL_CONFIG : "typed_config"
 11 | 
 12 |     LIBRARY_ITEM {
 13 |       bigint id PK
 14 |       bigint parent_id FK
 15 |       text absolute_path
 16 |       enum item_type
 17 |       enum status
 18 |       bigint initial_size_bytes
 19 |       bigint final_size_bytes
 20 |       int files_to_process_count
 21 |       text source_name
 22 |       text renamed_name
 23 |       text error_text
 24 |     }
 25 | 
 26 |     APP_CONFIGURATION {
 27 |       bigint id PK
 28 |       varchar section
 29 |       varchar config_key
 30 |       jsonb config_value
 31 |     }
 32 | 
 33 |     PLUGIN_REGISTRY {
 34 |       bigint id PK
 35 |       varchar plugin_code
 36 |       enum status
 37 |       varchar version
 38 |       text html_entrypoint
 39 |       text python_entrypoint
 40 |       varchar schema_name
 41 |     }
 42 | 
 43 |     PLUGIN_INSTANCE {
 44 |       bigint id PK
 45 |       bigint plugin_id FK
 46 |       varchar instance_name
 47 |       boolean is_enabled
 48 |       int priority
 49 |     }
 50 | 
 51 |     PLUGIN_DISCORD_CONFIG {
 52 |       bigint plugin_instance_id PK,FK
 53 |       text webhook_url
 54 |       varchar channel_name
 55 |       text message_template
 56 |     }
 57 | ```

## 📡 Typage des Objets Scannés

`library_item.item_type`:

- `FILE`
- `FOLDER`
- `ARCHIVE`

## 📡 Statuts Métiers

`library_item.status` couvre le workflow demandé:

1. `NEW`
2. `VALID`
3. `DECOMPRESSED`
4. `RENAMED`
5. `PROCESSING_PENDING`
6. `PROCESSING`
7. `PROCESSED`
8. `DELETED`
9. `ERROR`

### 📡 Règles Métier Associées

- Une archive décompressée reste le **même enregistrement** (`id` inchangé) avec:
  - `status = 'DECOMPRESSED'`
  - `item_type` mis à jour de `ARCHIVE` vers `FOLDER`.
- Après traitement réussi (génération du `.m4b`), l'élément bascule de `FOLDER` vers `FILE` avec `status = 'PROCESSED'`.
- La contrainte SQL `ck_library_item_processed_is_file` garantit que `PROCESSED => FILE`.
- En cas d'échec, `status = 'ERROR'` + détail dans `error_text`.
- Lors de suppression physique, marquer `status = 'DELETED'` et `deleted_at`.

## 📡 Mapping Explicite des Champs Demandés

Table cible: `library_item`

- Taille initiale → `initial_size_bytes`
- Taille finale → `final_size_bytes`
- Nombre de fichiers à traiter → `files_to_process_count`
- Nom d'origine (archive/dossier) → `source_name`
- Nom renommé (dossier/fichier) → `renamed_name`
- Erreur textuelle (état 9) → `error_text`

## 📡 Configuration Globale vs Configuration Plugin

### 1) Configuration Globale (`app_configuration`)

Utilisée pour les paramètres transverses:

- `general`
- `paths`
- `audio_processing`
- `audiobookshelf`
- `ollama`

⚠️ Une contrainte SQL bloque les sections `plugins.%` dans cette table.

### 2) Registre Plugins (`plugin_registry`)

Représente la zone UI sous la forme demandée:

- `plugins > INSTALLED - discord`
- `plugins > INSTALLED - telegram`
- `plugins > INSTALLED - email`

Le registre stocke:

- identité plugin (`plugin_code`, `display_name`),
- état d'installation (`INSTALLED`, `DISABLED`, `UNINSTALLED`, `ERROR`),
- métadonnées runtime (version, points d'entrée HTML/Python, schéma SQL).

### 3) Instances Plugin (`plugin_instance`)

Permet de configurer un plugin **plusieurs fois**:

- ex: `discord-prod`, `discord-staging`, `discord-alertes-critiques`.

Chaque instance est ensuite reliée à une table de config spécialisée.

### 4) Config Spécialisées par Plugin

- `plugin_discord_config`
- `plugin_telegram_config`
- `plugin_email_config`

Chaque table porte les champs techniques spécifiques au plugin et offre une validation forte (types/contraintes SQL).

## 📡 Suggestion d'Architecture d'un Plugin (Extensible)

Pour faciliter l'ajout de nouveaux plugins, standardiser un plugin en **3 briques** :

1. **Page HTML**
   - `plugins/<plugin_code>/templates/config.html`
   - Formulaire de gestion des `plugin_instance` + config spécialisée.

2. **SQL (Migration Plugin)**
   - `database/plugins/<plugin_code>/0001_init.sql`
   - Crée la table spécialisée `plugin_<plugin_code>_config`.

3. **Python Runtime**
   - `plugins/<plugin_code>/service.py`
   - Chargement des instances actives, validation config, exécution des actions.

### 📡 Contrat Minimal Recommandé pour un Nouveau Plugin

- Entrée dans `plugin_registry`.
- Support multi-instance via `plugin_instance`.
- Une table `plugin_<code>_config` (1:1 avec instance).
- Un endpoint API `GET/POST /api/plugins/<code>/instances`.
- Une page UI dédiée branchée sur cet endpoint.

## 📡 Migration SQL

La migration proposée est versionnée dans:

- `database/migrations/0003_input_inventory_and_configuration.sql`

Elle introduit:

- `library_item` + historique et contrainte `PROCESSED => FILE`
- `app_configuration` + historique (hors plugins)
- `plugin_registry`
- `plugin_instance`
- `plugin_discord_config`
- `plugin_telegram_config`
- `plugin_email_config`
- liaison `processing_job.library_item_id`

## 📝 Conclusion

Le plan de migration des données permet de préparer une transition fluide vers une architecture PostgreSQL. Les prochaines étapes consistent à valider ce plan et à commencer l'implémentation des nouvelles fonctionnalités.
