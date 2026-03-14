# Audiobook Master v3.0.0

> Architecture moderne de traitement audio avec FastAPI + Svelte + WebSocket

## 🎯 Vue d'Ensemble

Audiobook Master v3 est une refonte complète de l'application de traitement audio, utilisant une architecture moderne et des technologies web avancées pour offrir une expérience utilisateur exceptionnelle et des performances optimales.

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework** : FastAPI avec Python 3.11+
- **Base de données** : PostgreSQL avec SQLAlchemy async
- **WebSocket** : Communication temps réel
- **Authentication** : JWT avec refresh tokens
- **API Documentation** : Swagger/OpenUI automatique

### Frontend (Svelte)
- **Framework** : SvelteKit avec TypeScript
- **Styling** : Tailwind CSS avec design system personnalisé
- **State Management** : Stores Svelte réactifs
- **WebSocket Client** : Connexion temps réelle
- **Responsive Design** : Mobile-first avec dark mode

### Infrastructure
- **Containerisation** : Docker multi-stage builds
- **Orchestration** : Docker Compose
- **Monitoring** : Prometheus + Grafana
- **Database** : PostgreSQL persistant

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Node.js 18+ (pour développement frontend)
- Python 3.11+ (pour développement backend)

### Déploiement Local

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Nehwon/audiobook-master.git
   cd audiobook-master
   git checkout V3.0.0a
   ```

2. **Démarrer les services**
   ```bash
   cd v3
   docker compose up -d db
   ```

3. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Accéder à l'application**
   - Frontend : http://localhost:5173
   - API Docs : http://localhost:8000/docs
   - Health Check : http://localhost:8000/api/v1/health

## 📁 Structure du Projet

```
v3/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Configuration, database, security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/               # SvelteKit application
│   ├── src/
│   │   ├── lib/           # Components, stores, API
│   │   └── routes/        # SvelteKit pages
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile          # Frontend container
└── docker-compose.yml      # Orchestration des services
```

## 🌐 API Documentation

### Endpoints Principaux

#### Jobs
- `GET /api/v1/jobs` - Lister les jobs
- `POST /api/v1/jobs` - Créer un job
- `GET /api/v1/jobs/{id}` - Détails d'un job
- `PUT /api/v1/jobs/{id}` - Mettre à jour un job
- `DELETE /api/v1/jobs/{id}` - Supprimer un job
- `POST /api/v1/jobs/{id}/retry` - Réessayer un job
- `POST /api/v1/jobs/{id}/cancel` - Annuler un job

#### Packets
- `GET /api/v1/packets` - Lister les packets
- `POST /api/v1/packets` - Créer un packet
- `GET /api/v1/packets/{id}` - Détails d'un packet
- `PUT /api/v1/packets/{id}` - Mettre à jour un packet
- `DELETE /api/v1/packets/{id}` - Supprimer un packet
- `POST /api/v1/packets/{id}/publish` - Publier un packet

#### WebSocket
- `WS /ws` - Endpoint WebSocket temps réel

### Documentation Interactive
Accédez à la documentation Swagger complète : http://localhost:8000/docs

## 🔧 Configuration

### Variables d'Environnement

#### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/audiobook_v3
JWT_SECRET_KEY=votre-secret-key-tres-securise
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
LOG_LEVEL=INFO
DEBUG=true
```

#### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## 🧪 Tests

### Backend
```bash
cd backend
pytest
pytest --cov=app  # Avec couverture
```

### Frontend
```bash
cd frontend
npm test          # Tests unitaires
npm run test:e2e  # Tests E2E avec Playwright
```

## 📊 Monitoring

### Health Checks
- **Backend** : `/api/v1/health`
- **Database** : Vérification connexion PostgreSQL
- **WebSocket** : Status des connexions actives

### Métriques
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000
- **Dashboard** : Métriques temps réel

## 🔒 Sécurité

### Authentication
- JWT access tokens (30 minutes)
- JWT refresh tokens (7 jours)
- Password hashing avec bcrypt
- CORS configuration restrictive

### Best Practices
- Validation Pydantic sur tous les inputs
- SQL injection prevention avec SQLAlchemy
- HTTPS en production
- Rate limiting sur les endpoints sensibles

## 🚀 Déploiement

### Docker Production
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Environment Variables
Configurez les variables d'environnement de production avant le déploiement.

### Health Checks
Les conteneurs incluent des health checks pour monitoring.

## 🔄 Migration depuis v2

### Changements Majeurs
- Architecture microservices
- Base de données PostgreSQL (remplace SQLite)
- API REST complète
- Frontend SPA (remplace Flask templates)
- WebSocket temps réel

### Guide de Migration
1. Exporter les données existantes
2. Importer dans PostgreSQL
3. Mettre à jour les configurations
4. Redéployer avec v3

## 📚 Documentation

- [Architecture Decision Records](docs/ADR-001-architecture-v3.md)
- [Frontend Design Choices](docs/ADR-002-frontend-design-choices.md)
- [WebSocket Events](docs/RFC-001-evenements-json.md)
- [MVP Backlog](docs/MVP-backlog-phase0.md)

## 🤝 Contribuer

1. Forker le projet
2. Créer une branche `feature/nom-de-la-feature`
3. Committer les changements
4. Pousser vers la branche
5. Créer une Pull Request

## 📄 License

Ce projet est sous license AGPL-3.0. Voir [LICENSE](LICENSE) pour les détails.

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/Nehwon/audiobook-master/issues)
- **Documentation** : [Wiki du projet](https://github.com/Nehwon/audiobook-master/wiki)
- **Discussions** : [GitHub Discussions](https://github.com/Nehwon/audiobook-master/discussions)

---

**Audiobook Master v3** - Le futur du traitement audio moderne 🎧✨
