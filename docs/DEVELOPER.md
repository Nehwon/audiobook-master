# 📚 Documentation Technique - Audiobook Manager Pro

Documentation complète de l'architecture, API et contribution pour développeurs.

---

## 🏗️ **Architecture Technique**

### 📁 **Structure du Projet**

```
audiobook-manager/
├── 📁 core/                    # Modules principaux
│   ├── config.py              # Configuration et variables d'environnement
│   ├── main.py                # Point d'entrée principal
│   ├── metadata.py             # Gestion des métadonnées audio
│   └── processor.py            # Traitement audio multithread
├── 📁 web/                     # Interface web
│   ├── app.py                 # Application Flask principale
│   └── templates/             # Templates HTML
├── 📁 gui/                     # Interface desktop
│   └── desktop_app.py         # Application Tkinter
├── 📁 integrations/             # Intégrations tierces
│   ├── audiobookshelf.py      # Client Audiobookshelf
│   ├── audiobookshelf_client.py # Client API complet
│   ├── config.py              # Configuration intégrations
│   └── sync_manager.py        # Gestion synchronisation
├── 📁 tests/                    # Suite de tests
├── 📁 scripts/                  # Scripts utilitaires
├── 📁 docs/                     # Documentation détaillée
├── 📁 data/                     # Données utilisateur
└── 📁 logs/                     # Logs applicatifs
```

### 🔧 **Modules Principaux**

#### **core/processor.py**
- **Multithreading CPU** : 32 workers pour double Xeon
- **5 stratégies adaptatives** : codec_only, reduce_bitrate, reduce_sample_rate, reduce_both, upgrade_needed
- **Phase 1/2/3** : Concaténation, encodage, finalisation
- **Monitoring temps réel** : Progression par fichier

#### **core/metadata.py**
- **Scrapers multiples** : Audible, Babelio, etc.
- **Enrichissement automatique** : Métadonnées intelligentes
- **Support multi-formats** : MP3, M4B, FLAC, WAV
- **Validation qualité** : Standards EBU R128

#### **web/app.py**
- **Flask + SocketIO** : Interface web temps réel
- **Endpoints REST** : `/health`, `/api/status`, `/api/convert`
- **WebSocket events** : Progression conversion en temps réel
- **Configuration flexible** : Variables d'environnement

#### **gui/desktop_app.py**
- **Tkinter moderne** : Interface desktop multi-onglets
- **Progression détaillée** : Barres, logs, métriques
- **Configuration avancée** : Bitrate, sample rate, loudnorm
- **Gestion erreurs** : Messages clairs et actions automatiques

#### **integrations/audiobookshelf_client.py**
- **Client API complet** : Authentification Bearer token
- **CRUD bibliothèques** : Create, Read, Update, Delete
- **Upload automatique** : Métadonnées + fichiers
- **Synchronisation bidirectionnelle** : Local ↔ distant
- **Gestion des conflits** : Skip/overwrite/merge

---

## 🔌 **API Documentation**

### **Endpoints Principaux**

#### **Health Checks**
```http
GET /health
{
  "service": "audiobook-manager-pro",
  "status": "healthy",
  "version": "2.1.0",
  "timestamp": "2026-03-04T12:00:00Z",
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 23.5,
    "disk_usage": {"percent": 78.1}
  },
  "directories": {
    "/app/data/source": "accessible",
    "/app/data/output": "accessible",
    "/app/temp": "accessible"
  }
}
```

#### **Status API**
```http
GET /api/status
{
  "api": "operational",
  "docker": {
    "container": "audiobook-manager",
    "image": "audiobook-manager-pro:v2.1.0",
    "port": 5000,
    "workers": 16,
    "threads": 8
  },
  "load_average": [1.2, 1.5, 1.4],
  "processes": 1,
  "uptime": 1234567.0
}
```

#### **WebSocket Events**
```javascript
// Connexion WebSocket
const socket = io('http://localhost:5000');

// Événement progression conversion
socket.on('conversion_progress', (data) => {
  console.log(`Progression: ${data.progress}%`);
  console.log(`Fichier actuel: ${data.current_file}`);
});

// Événement conversion terminée
socket.on('conversion_complete', (data) => {
  console.log(`Conversion terminée: ${data.output_file}`);
});

// Événement erreur
socket.on('conversion_error', (data) => {
  console.error(`Erreur: ${data.error_message}`);
});
```

---

## 🐳 **Docker & Déploiement**

### **Dockerfile**
```dockerfile
# Base image Python 3.11 slim
FROM python:3.11-slim

# Installation FFmpeg et dépendances
RUN apt-get update && apt-get install -y \
    ffmpeg libavcodec-extra libavformat-dev \
    build-essential curl wget git

# Configuration utilisateur
RUN groupadd -r audiobook && useradd -r -g audiobook -d /app audiobook
WORKDIR /app

# Installation dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copie code source
COPY . .
RUN chown -R audiobook:audiobook /app

# Configuration volumes et ports
VOLUME ["/app/data", "/app/logs", "/app/temp"]
EXPOSE 5000

# Point d'entrée
USER audiobook
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["web"]
```

### **Docker Compose**
```yaml
version: '3.8'
services:
  audiobook-manager:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data/source:/app/data/source
      - ./data/output:/app/data/output
      - ./logs:/app/logs
    environment:
      - MAX_WORKERS=16
      - CPU_THREADS=8
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 🧪 **Tests et Qualité**

### **Structure des Tests**
```
tests/
├── test_config.py              # Tests configuration
├── test_main.py               # Tests module principal
├── test_processor.py           # Tests traitement audio
├── test_metadata.py            # Tests métadonnées
├── integration/
│   └── test_integration.py   # Tests d'intégration
└── coverage/                  # Rapports de couverture
```

### **Exécution des Tests**
```bash
# Tests unitaires
python -m pytest tests/ -v --cov=core --cov-report=html

# Tests d'intégration
python -m pytest tests/integration/ -v --cov=integrations

# Tests performance
python -m pytest tests/test_performance.py -v --benchmark-only

# Rapport de couverture
open htmlcov/index.html
```

### **Qualité Code**
```bash
# Linting
flake8 core/ web/ gui/ integrations/

# Formatage
black core/ web/ gui/ integrations/

# Typage
mypy core/ web/ gui/ integrations/

# Sécurité
bandit -r core/ web/ gui/ integrations/
safety check -r requirements.txt
```

---

## 🔧 **Configuration**

### **Variables d'Environnement**
```bash
# Répertoires
AUDIOBOOK_SOURCE_DIR=/home/user/Audiobooks
AUDIOBOOK_OUTPUT_DIR=/home/user/Audiobooks_Processed
AUDIOBOOK_TEMP_DIR=/tmp/audiobooks_web

# Performance
MAX_WORKERS=16
CPU_THREADS=8
GPU_ENABLED=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/audiobook.log

# Audiobookshelf
AUDIOBOOKSHELF_HOST=localhost
AUDIOBOOKSHELF_PORT=13378
AUDIOBOOKSHELF_USERNAME=admin
AUDIOBOOKSHELF_PASSWORD=password
AUDIOBOOKSHELF_ENABLED=true
```

### **Fichier de Configuration**
```json
{
  "processing": {
    "max_workers": 16,
    "cpu_threads": 8,
    "gpu_enabled": false,
    "temp_dir": "/tmp/audiobooks_web"
  },
  "audio": {
    "default_bitrate": 128000,
    "sample_rate": 44100,
    "loudnorm": {
      "target_i": -18,
      "target_lra": 11,
      "target_tp": -1.5
    }
  },
  "audiobookshelf": {
    "host": "localhost",
    "port": 13378,
    "username": "admin",
    "password": "password",
    "enabled": true,
    "auto_sync": true,
    "library_id": "default"
  }
}
```

---

## 🤝 **Guide de Contribution**

### **Workflow de Développement**
1. **Fork** le projet sur GitHub
2. **Créer branche** feature/nom-fonctionnalité
3. **Développer** avec tests unitaires
4. **Tester** localement avec `pytest`
5. **Commit** avec messages clairs
6. **Push** vers branche feature
7. **Pull Request** vers main

### **Standards de Code**
- **Python 3.8+** compatible
- **Type hints** obligatoires
- **Docstrings** Google style
- **Tests** >80% couverture
- **Linting** Flake8 compliant

### **Messages de Commit**
```
feat: ajout nouvelle fonctionnalité X
fix: correction bug Y
docs: mise à jour documentation
test: ajout tests pour Z
refactor: optimisation code W
chore: maintenance dépendances
```

---

## 🚀 **Déploiement Production**

### **Prérequis**
- **Docker 20.10+**
- **Docker Compose 2.0+**
- **CPU 4+ cœurs** recommandé
- **RAM 8GB+** recommandé
- **Stockage 50GB+** SSD recommandé

### **Installation Production**
```bash
# Clone repository
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master

# Configuration environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Déploiement
docker-compose -f docker-compose.prod.yml up -d

# Vérification santé
curl http://localhost:5000/health
```

### **Monitoring Production**
```bash
# Logs temps réel
docker-compose logs -f audiobook-manager

# Métriques système
curl http://localhost:5000/api/status

# Backup données
docker-compose exec audiobook-manager tar -czf /backup/data-$(date +%Y%m%d).tar.gz /app/data
```

---

## 🐛 **Dépannage Avancé**

### **Problèmes Communs**

#### **Memory Leak**
```bash
# Diagnostic mémoire
docker stats audiobook-manager
python -m memory_profiler core/processor.py

# Solution : Limiter workers
MAX_WORKERS=8 python3 -m core.main
```

#### **Performance CPU**
```bash
# Monitoring CPU
htop
docker exec audiobook-manager top

# Solution : Optimiser threads
CPU_THREADS=4 python3 -m core.main
```

#### **Docker Build Lent**
```bash
# Optimisation build
docker build --no-cache --progress=plain .
docker buildx build --platform linux/amd64,linux/arm64 .
```

### **Logs et Debug**
```bash
# Logs détaillés
LOG_LEVEL=DEBUG python3 -m core.main

# Logs Docker
docker-compose logs audiobook-manager --tail=100

# Debug mode
python3 -m pdb core.main
```

---

## 📞 **Support et Communauté**

### **Obtenir de l'Aide**
- **Documentation** : https://docs.audiobook-manager.pro
- **Issues GitHub** : https://github.com/Nehwon/audiobook-master/issues
- **Discord** : https://discord.gg/audiobook-manager
- **Email** : support@audiobook-manager.pro

### **Rapporter un Bug**
1. **Vérifier** issues existantes
2. **Créer nouvelle issue** avec template
3. **Inclure** : version, OS, logs, steps to reproduce
4. **Ajouter** tags : bug, enhancement, question

### **Proposer une Feature**
1. **Discuter** sur Discord ou GitHub Discussions
2. **Créer issue** avec template feature-request
3. **Décrire** cas d'usage et bénéfices
4. **Soumettre** Pull Request avec implémentation

---

*Documentation technique maintenue activement • Dernière mise à jour : 4 Mars 2026* 📚✨

*Pour contribuer au projet, consultez le [Guide de Contribution](https://github.com/Nehwon/audiobook-master/blob/main/CONTRIBUTING.md)*
