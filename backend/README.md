# Audiobook Master v3 - Backend FastAPI

**Architecture moderne** : FastAPI + PostgreSQL + WebSocket temps réel  
**Version** : 3.0.0-alpha.1  
**Statut** : En développement  

---

## 🏗️ Architecture

```text
[Frontend Svelte]
          |
   (WebSocket + HTTP)
          |
[FastAPI: REST + WS Gateway]
          |
[PostgreSQL]
   |  triggers + pg_notify
   +-----------------------> [FastAPI Notifier -> Broadcast WS]
```

## 📁 Structure du Projet

```
v3/backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py      # Endpoints jobs
│   │   │   ├── packets.py   # Endpoints packets
│   │   │   ├── monitoring.py # Endpoints monitoring
│   │   │   └── websocket.py # WebSocket gateway
│   │   └── dependencies.py # Dépendances API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   ├── security.py       # Authentification
│   │   └── events.py         # Gestion événements
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py           # Models Job
│   │   ├── packet.py        # Models Packet
│   │   └── base.py          # Models de base
│   ├── services/
│   │   ├── __init__.py
│   │   ├── job_service.py   # Service Job
│   │   ├── packet_service.py # Service Packet
│   │   ├── notification_service.py # Notifications
│   │   └── postgres_notifier.py # PostgreSQL -> WS
│   └── db/
│       ├── __init__.py
│       ├── base.py          # Base SQLAlchemy
│       ├── session.py       # Session management
│       └── migrations/       # Alembic migrations
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Démarrage Rapide

### Installation
```bash
# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dépendances
pip install -r requirements.txt
```

### Configuration
```bash
# Variables d'environnement
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/audiobook_v3"
export JWT_SECRET_KEY="votre-secret-key"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Lancement
```bash
# Développement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API Endpoints

### REST API
- `GET /api/v1/health` - Health check
- `GET /api/v1/jobs` - Lister les jobs
- `POST /api/v1/jobs` - Créer un job
- `GET /api/v1/jobs/{id}` - Détail job
- `PUT /api/v1/jobs/{id}` - Mettre à jour job
- `DELETE /api/v1/jobs/{id}` - Supprimer job

### WebSocket
- `WS /ws` - WebSocket temps réel

## 🔧 Configuration

### FastAPI Settings
```python
# app/core/config.py
class Settings:
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list = ["http://localhost:5173"]  # Frontend Svelte
```

### PostgreSQL Setup
```sql
-- Créer la base de données
CREATE DATABASE audiobook_v3;

-- Extensions requises
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_notify";
```

## 📡 WebSocket Events

### Format des événements
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

### Exemples
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
    "progress": 45
  }
}
```

## 🐳 Docker

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./v3/backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/audiobook_v3
      - JWT_SECRET_KEY=votre-secret-key
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=audiobook_v3
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🧪 Tests

### Tests Unitaires
```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_api/test_jobs.py -v
```

### Tests WebSocket
```bash
# Tests WebSocket
pytest tests/test_websocket.py -v
```

## 📊 Monitoring

### Health Endpoints
- `GET /health` - Health check simple
- `GET /health/detailed` - Health check détaillé
- `GET /metrics` - Métriques Prometheus

### Logs
```python
# Configuration logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

## 🔐 Sécurité

### JWT Authentication
```python
# Access token (30 minutes)
# Refresh token (7 jours)

# Headers
Authorization: Bearer <access_token>
```

### CORS
```python
# Configuration pour frontend Svelte
origins = [
    "http://localhost:5173",  # Développement
    "https://v3.audiobook-master.com",  # Production
]
```

## 🚀 Déploiement

### Production
```bash
# Build image
docker build -t audiobook-v3-backend .

# Run container
docker run -d \
  --name audiobook-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e JWT_SECRET_KEY=... \
  audiobook-v3-backend
```

### Environment Variables
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
JWT_SECRET_KEY=votre-secret-très-sécurisé
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://v3.audiobook-master.com"]
LOG_LEVEL=INFO
```

## 📝 Développement

### Code Style
```bash
# Formatage
black app/
isort app/

# Linting
flake8 app/
mypy app/

# Tests
pytest --cov=app
```

### Pre-commit
```bash
# Installation pre-commit
pre-commit install

# Exécution manuelle
pre-commit run --all-files
```

## 🔄 Migration depuis v2

### Points d'attention
- Nouvelle structure de base de données
- Changement de format d'API
- WebSocket au lieu de polling
- JWT au lieu de sessions

### Script de migration
```python
# scripts/migrate_v2_to_v3.py
# TODO: Implémenter la migration des données
```

---

**Statut**: 🚧 **En développement** - Phase 1 en cours
