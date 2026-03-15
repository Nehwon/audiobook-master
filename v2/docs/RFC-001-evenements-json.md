# RFC-001: Contrat d'Événements JSON v1

**Status**: Proposed  
**Date**: 2026-03-14  
**Version**: 1.0  
**Auteur**: Architecture Team  

---

## Objectif

Définir un contrat d'événements standard pour la communication temps réel entre le backend FastAPI et le frontend React/Svelte via WebSocket.

## Spécification

### Format de Base

```json
{
  "schema_version": 1,
  "event_id": "uuid",
  "event_type": "insert|update|delete",
  "entity": "job|packet|folder|error|notification",
  "entity_id": "string",
  "timestamp": "ISO-8601",
  "payload": {}
}
```

### Champs Détaillés

#### `schema_version` (obligatoire)
- **Type**: Integer
- **Description**: Version du schéma d'événements
- **Valeur actuelle**: 1
- **Raison**: Permettre l'évolution du format sans casser la compatibilité

#### `event_id` (obligatoire)
- **Type**: UUID v4
- **Description**: Identifiant unique de l'événement
- **Format**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Raison**: Traçabilité et déduplication

#### `event_type` (obligatoire)
- **Type**: String
- **Description**: Type d'opération sur l'entité
- **Valeurs possibles**:
  - `insert`: Création d'une nouvelle entité
  - `update`: Modification d'une entité existante
  - `delete`: Suppression d'une entité
- **Raison**: Filtrage et traitement côté client

#### `entity` (obligatoire)
- **Type**: String
- **Description**: Type d'entité concernée
- **Valeurs possibles**:
  - `job`: Job de traitement audio
  - `packet`: Paquet de fichiers pour publication
  - `folder`: Dossier source traité
  - `error`: Erreur système ou utilisateur
  - `notification`: Notification système
  - `user_activity`: Activité utilisateur
- **Raison**: Routage et traitement spécialisé

#### `entity_id` (obligatoire)
- **Type**: String
- **Description**: Identifiant de l'entité concernée
- **Format**: Variable selon type (UUID, ID numérique, chemin)
- **Exemples**:
  - Job: `"12345"`
  - Packet: `"packet-uuid-xxxx"`
  - Folder: `"/path/to/folder"`
- **Raison**: Liaison avec les données existantes

#### `timestamp` (obligatoire)
- **Type**: String (ISO-8601)
- **Description**: Moment de création de l'événement
- **Format**: `"2026-03-14T12:30:45.123Z"`
- **Raison**: Ordering et synchronisation temporelle

#### `payload` (obligatoire)
- **Type**: Object
- **Description**: Données spécifiques à l'entité et l'événement
- **Contenu**: Variable selon `entity` et `event_type`
- **Raison**: Transport des données métier

## Exemples d'Usage

### Insertion d'un Job

```json
{
  "schema_version": 1,
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "insert",
  "entity": "job",
  "entity_id": "12345",
  "timestamp": "2026-03-14T12:30:45.123Z",
  "payload": {
    "status": "queued",
    "source_path": "/audio/book-1",
    "output_path": "/output/book-1.m4b",
    "created_at": "2026-03-14T12:30:45.000Z"
  }
}
```

### Mise à jour d'un Packet

```json
{
  "schema_version": 1,
  "event_id": "660e8400-e29b-41d4-a716-446655440001",
  "event_type": "update",
  "entity": "packet",
  "entity_id": "packet-660e8400-e29b",
  "timestamp": "2026-03-14T12:35:22.456Z",
  "payload": {
    "status": "published",
    "published_at": "2026-03-14T12:35:22.000Z",
    "channels": ["discord", "telegram"],
    "changelog_message": "Nouveau livre audio disponible"
  }
}
```

### Erreur Système

```json
{
  "schema_version": 1,
  "event_id": "770e8400-e29b-41d4-a716-446655440002",
  "event_type": "insert",
  "entity": "error",
  "entity_id": "error-770e8400-e29b",
  "timestamp": "2026-03-14T12:40:15.789Z",
  "payload": {
    "error_code": "AUDIO_CONVERSION_FAILED",
    "message": "Échec de conversion audio",
    "component": "processor",
    "job_id": "12345",
    "stack_trace": "...",
    "severity": "error"
  }
}
```

## Payloads par Entité

### Job
```json
{
  "status": "queued|running|done|failed",
  "source_path": "string",
  "output_path": "string",
  "progress": 0-100,
  "error_message": "string|null",
  "created_at": "ISO-8601",
  "started_at": "ISO-8601|null",
  "completed_at": "ISO-8601|null"
}
```

### Packet
```json
{
  "status": "draft|ready|published|failed",
  "files": ["file1.m4b", "file2.m4b"],
  "metadata": {},
  "published_at": "ISO-8601|null",
  "channels": ["discord", "telegram", "email"],
  "changelog_message": "string"
}
```

### Folder
```json
{
  "path": "string",
  "status": "scanned|processing|done|error",
  "file_count": 0-999,
  "total_size": 0-999999999,
  "last_scan": "ISO-8601"
}
```

### Error
```json
{
  "error_code": "string",
  "message": "string",
  "component": "processor|web|database|integration",
  "severity": "info|warning|error|critical",
  "job_id": "string|null",
  "stack_trace": "string|null",
  "user_id": "string|null"
}
```

## Règles de Validation

### Coté Backend (Émission)
1. **Schema version**: Toujours incluse et valide
2. **Event ID**: UUID v4 unique et valide
3. **Event type**: Valeur parmi la liste autorisée
4. **Entity**: Valeur parmi la liste autorisée
5. **Timestamp**: Format ISO-8601 valide
6. **Payload**: Structure valide pour l'entité

### Coté Frontend (Réception)
1. **Version check**: Rejeter si `schema_version` > supportée
2. **Event ID**: Vérifier unicité dans la session
3. **Type filtering**: Traiter selon `event_type`
4. **Entity routing**: Router vers le bon composant
5. **Timestamp**: Utiliser pour ordering et mise à jour
6. **Payload validation**: Valider structure avant traitement

## Évolution du Schema

### Versioning
- **Changement majeur**: Incrémenter `schema_version`
- **Changement mineur**: Garder même version
- **Compatibilité**: Supporter N-1 versions pendant 6 mois

### Exemple d'évolution v2
```json
{
  "schema_version": 2,
  "event_id": "uuid",
  "event_type": "insert|update|delete|batch",
  "entity": "job|packet|folder|error|notification|user",
  "entity_id": "string",
  "timestamp": "ISO-8601",
  "payload": {},
  "metadata": {
    "source": "postgresql-trigger|manual|system",
    "priority": "low|medium|high|critical"
  }
}
```

## Implémentation

### Backend FastAPI
```python
class EventSchema(BaseModel):
    schema_version: int = 1
    event_id: str
    event_type: Literal["insert", "update", "delete"]
    entity: Literal["job", "packet", "folder", "error", "notification"]
    entity_id: str
    timestamp: datetime
    payload: Dict[str, Any]
```

### Frontend React/Svelte
```typescript
interface EventMessage {
  schemaVersion: number;
  eventId: string;
  eventType: 'insert' | 'update' | 'delete';
  entity: 'job' | 'packet' | 'folder' | 'error' | 'notification';
  entityId: string;
  timestamp: string;
  payload: Record<string, any>;
}
```

## Tests

### Cas de test obligatoires
1. **Validation format**: Message mal formé rejeté
2. **Version mismatch**: Version supérieure rejetée
3. **Event type invalide**: Type inconnu ignoré
4. **Payload manquant**: Message avec payload vide
5. **Timestamp invalide**: Format date incorrect

## Sécurité

### Validation d'entrée
- Échapper toutes les chaînes JSON
- Valider les UUID avec regex
- Limiter la taille des payloads (max 1MB)

### Rate limiting
- Maximum 100 events/secondes par connexion
- Rejet si limite dépassée

---

**Statut**: ✅ **PROPOSÉ** - Prêt pour implémentation Phase 2
