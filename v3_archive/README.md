# Audiobook Master v3

**Architecture moderne** : FastAPI + PostgreSQL + Svelte + WebSocket temps réel  
**Version** : 3.0.0-alpha.1  
**Statut** : En développement  

---

## 🚀 Vue d'Ensemble

Audiobook Master v3 représente une réécriture complète de l'application avec une architecture moderne et scalable. Cette version sépare complètement le code de la version v2 pour éviter tout mélange et permettre une évolution indépendante.

### 🏗️ Architecture

```text
[Svelte Frontend] ←→ [FastAPI Backend] ←→ [PostgreSQL]
       ↓                    ↓                      ↓
   Tailwind CSS        WebSocket            Triggers
   Stores             Temps réel            pg_notify
```

### 📁 Structure du Projet

```
v3/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # Endpoints REST
│   │   ├── core/      # Configuration core
│   │   ├── models/    # SQLAlchemy models
│   │   ├── services/  # Business logic
│   │   └── db/        # Database setup
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/          # Svelte application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── stores/    # Svelte stores
│   │   │   ├── api/       # API client
│   │   │   └── components/ # UI components
│   │   └── routes/         # SvelteKit routes
│   ├── package.json
│   ├── Dockerfile
│   └── README.md
├── docker-compose.yml
└── README.md
```

---

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose
- Node.js 18+ (pour développement local)
- Python 3.11+ (pour développement local)

### Avec Docker (Recommandé)

```bash
# Clone le repository
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master/v3

# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Logs
docker-compose logs -f
```

**Accès aux services** :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- API Documentation : http://localhost:8000/docs
- Grafana (monitoring) : http://localhost:3001 (profile monitoring)

### Développement Local

#### Backend
```bash
cd v3/backend

# Environnement virtuel
python -m venv venv
source venv/bin/activate

# Dépendances
pip install -r requirements.txt

# Configuration
export DATABASE_URL="postgresql+asyncpg://postgres:audiobook123@localhost:5432/audiobook_v3"
export JWT_SECRET_KEY="votre-secret-key"

# Démarrer
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd v3/frontend

# Dépendances
npm install

# Développement
npm run dev

# Build production
npm run build
```

---

## 📡 API Documentation

### Endpoints Principaux

#### Health Check
```bash
GET /api/v1/health
```

#### Jobs
```bash
GET    /api/v1/jobs          # Lister les jobs
POST   /api/v1/jobs          # Créer un job
GET    /api/v1/jobs/{id}     # Détail job
PUT    /api/v1/jobs/{id}     # Mettre à jour job
DELETE /api/v1/jobs/{id}     # Supprimer job
```

#### Packets
```bash
GET    /api/v1/packets       # Lister les packets
POST   /api/v1/packets       # Créer un packet
GET    /api/v1/packets/{id}  # Détail packet
PUT    /api/v1/packets/{id}  # Mettre à jour packet
DELETE /api/v1/packets/{id}  # Supprimer packet
```

#### WebSocket
```bash
WS /ws                       # WebSocket temps réel
```

### Documentation Interactive
Ouvrez http://localhost:8000/docs pour la documentation Swagger interactive.

---

## 🔄 WebSocket Events

### Format des Événements

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

### Types d'Événements

#### Job Update
```json
{
  "schema_version": 1,
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "update",
  "entity": "job",
  "entity_id": "12345",
  "timestamp": "2026-03-14T12:30:45.123Z",
  "payload": {
    "status": "running",
    "progress": 45,
    "started_at": "2026-03-14T12:30:40.000Z"
  }
}
```

#### Notification
```json
{
  "schema_version": 1,
  "event_id": "660e8400-e29b-41d4-a716-446655440001",
  "event_type": "insert",
  "entity": "notification",
  "entity_id": "notif-660e8400-e29b",
  "timestamp": "2026-03-14T12:35:22.456Z",
  "payload": {
    "type": "success",
    "title": "Job complété",
    "message": "Le job #12345 a été traité avec succès",
    "user_id": "user-123"
  }
}
```

---

## 🎨 Frontend Svelte

### Stores Principaux

#### authStore
```javascript
import { authStore } from '$lib/stores/authStore.js';

// Login
await authStore.login({ username, password });

// Logout
authStore.logout();

// État
$authStore.isAuthenticated
$authStore.user
```

#### jobStore
```javascript
import { jobStore, activeJobs, failedJobs } from '$lib/stores/jobStore.js';

// Récupérer les jobs
await jobStore.fetchJobs();

// Créer un job
const job = await jobStore.createJob(jobData);

// Stores dérivés
$activeJobs    // Jobs en cours
$failedJobs    // Jobs en erreur
```

### Composants UI

#### Button
```svelte
<Button variant="primary" size="md" onclick={handleClick}>
  Créer un Job
</Button>
```

#### Loading
```svelte
<Loading size="lg" text="Traitement en cours..." />
```

---

## 🗄️ Database Schema

### Tables Principales

#### jobs
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    source_path VARCHAR(500) NOT NULL,
    output_path VARCHAR(500),
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

#### packets
```sql
CREATE TABLE packets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    files TEXT[],
    metadata JSONB,
    published_at TIMESTAMP,
    channels VARCHAR[],
    changelog_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Triggers PostgreSQL

Les triggers PostgreSQL créent automatiquement des événements `pg_notify` pour les changements en base de données.

---

## 🔧 Configuration

### Variables d'Environnement

#### Backend
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/audiobook_v3
JWT_SECRET_KEY=votre-secret-très-sécurisé
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
```

#### Frontend
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 🧪 Tests

### Backend
```bash
cd v3/backend

# Tests unitaires
pytest

# Tests avec couverture
pytest --cov=app --cov-report=html

# Tests WebSocket
pytest tests/test_websocket.py -v
```

### Frontend
```bash
cd v3/frontend

# Tests composants
npm run test

# Tests E2E
npm run test:e2e

# Couverture
npm run test:coverage
```

---

## 📊 Monitoring

### Métriques Disponibles

#### Backend
- Health check endpoints
- Prometheus metrics
- Structured logging

#### Frontend
- Performance monitoring
- Error tracking (Sentry)
- User analytics

### Dashboard Grafana

Avec le profile `monitoring` :
- Grafana : http://localhost:3001 (admin/admin123)
- Prometheus : http://localhost:9090

---

## 🚀 Déploiement

### Production avec Docker

```bash
# Build et déploiement
docker-compose -f docker-compose.yml up -d

# Avec monitoring
docker-compose --profile monitoring up -d
```

### Configuration Production

#### Sécurité
- Utiliser des secrets forts pour JWT
- Configurer HTTPS avec reverse proxy
- Limiter les origins CORS

#### Performance
- Configurer les connexions PostgreSQL
- Activer le cache Redis
- Optimiser les images Docker

---

## 🔄 Migration depuis v2

### Points Clés
- Architecture complètement séparée
- Nouveau format d'API
- WebSocket au lieu de polling
- JWT au lieu de sessions
- Base de données PostgreSQL

### Script de Migration
```bash
# TODO: Créer un script de migration
# v2/v3-migration/migrate_data.py
```

---

## 📝 Développement

### Code Style
- Backend : `black`, `isort`, `flake8`, `mypy`
- Frontend : `prettier`, `eslint`, `svelte-check`

### Git Hooks
```bash
# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Contributions
1. Forker le repository
2. Créer une branche `feature/nom-feature`
3. Suivre le code style
4. Ajouter des tests
5. Soumettre une Pull Request

---

## 📞 Support

### Documentation
- Backend : `v3/backend/README.md`
- Frontend : `v3/frontend/README.md`
- API : http://localhost:8000/docs

### Issues
- GitHub Issues : https://github.com/Nehwon/audiobook-master/issues
- Discussions : https://github.com/Nehwon/audiobook-master/discussions

---

## 📋 Roadmap

### Phase 1 (En cours)
- [x] Architecture de base
- [x] Structure projet v3
- [ ] Backend FastAPI endpoints
- [ ] WebSocket implementation
- [ ] Frontend Svelte de base

### Phase 2 (Prochaine)
- [ ] Interface complète
- [ ] Tests automatisés
- [ ] Documentation API
- [ ] Monitoring avancé

### Phase 3 (Future)
- [ ] Multi-tenant
- [ ] Plugin system
- [ ] Advanced analytics
- [ ] Mobile app

---

**Statut**: 🚧 **En développement actif** - Phase 1 en cours

---

*Pour plus d'informations, consultez les README spécifiques dans `backend/` et `frontend/`.*
