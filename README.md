# 🎧 Audiobook Manager Pro

Système professionnel de traitement d'audiobooks avec multithreading CPU optimisé, interface graphique desktop et synchronisation Audiobookshelf.

## 🚀 **Version 2.1.0 - Dockerisation & Interface Graphique & Synchronisation**

### ✅ **Nouvelles Fonctionnalités Majeures**

#### 🐳 **Dockerisation Complète**
- **Dockerfile** : Configuration complète avec FFmpeg 7.1.3 et dépendances
- **Docker Compose** : Services (app, monitoring, BDD, Redis) avec paramètres `.env`
- **Multi-plateforme** : Support Linux/Windows/macOS
- **Health checks** : Endpoints `/health` et `/api/status`
- **Installation one-click** : Script automatisé multi-OS
- **Interface web simple** : `simple_web.py` pour monitoring basique
- **Registry GHCR** : Images GitHub Container Registry intégrées
- **Workflow GitHub Actions** : Build Docker automatisé

#### 🖥️ **Interface Graphique Desktop**
- **Application Tkinter** : Interface moderne et intuitive (`gui/desktop_app.py`)
- **Progression temps réel** : Barres, logs, status détaillés
- **Configuration avancée** : Bitrate, sample rate, GPU, loudnorm
- **Gestion erreurs** : Messages clairs et actions automatiques
- **Packaging multi-OS** : Exécutables autonomes

#### 🔗 **Intégration Audiobookshelf**
- **Client API complet** : Authentification, upload, recherche (`integrations/audiobookshelf_client.py`)
- **Synchronisation automatique** : Métadonnées + fichiers (`integrations/sync_manager.py`)
- **Configuration flexible** : Fichier JSON + variables d'environnement (`integrations/config.py`)
- **Gestion des conflits** : Skip/overwrite/merge
- **Support multi-bibliothèques** : CRUD complet

#### 🔄 **CI/CD Intégral**
- **Workflows Gitea** : Build Docker automatique (`.gitea/workflows/`)
- **Workflows GitHub** : Build Docker automatisé avec GitHub Actions
- **Tests complets** : Unitaires, intégration, performance (`tests/`)
- **Sécurité intégrée** : Trivy, Bandit, Safety, SBOM
- **Déploiement automatisé** : Staging/production
- **Releases GitHub** : Assets multi-plateformes
- **Smart folder renaming** : Renommage intelligent avec apostrophes normalisées

---

## 🎯 **Performance Exceptionnelle**

### ⚡ **Multithreading CPU Optimisé**
- **Double Xeon 32 cœurs** : 32 workers parallèles
- **Performance mesurée** : 3.5x plus rapide que séquentiel
- **81 fichiers** : 634.7MB → 652.3MB en 25min15s
- **CPU optimisé** : 100% utilisation double Xeon

### 🎵 **Standards Audio Professionnels**
- **EBU R128** : -18 LUFS / 11 LU LRA / TP -1.5
- **AAC 128k** : Haute qualité optimisée
- **48kHz** : Sample rate standard audiobooks
- **5 stratégies adaptatives** : codec_only, reduce_bitrate, etc.

---

## 🛠️ **Installation Rapide**

### 🚀 **Installation One-Click**
```bash
# Installation automatique multi-plateforme
curl -fsSL https://raw.githubusercontent.com/Nehwon/audiobook-master/main/scripts/install.sh | bash
```

### 🐳 **Installation Docker**
```bash
# Clone et démarrage
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master
docker build -t audiobook-manager-pro:v2.1.0 .
docker run -d --name audiobook-manager -p 5000:5000 \
  -v $(pwd)/data/source:/app/data/source \
  -v $(pwd)/data/output:/app/data/output \
  audiobook-manager-pro:v2.1.0

# Avec Docker Compose
docker-compose up -d

# Avec monitoring inclus
docker-compose --profile monitoring up -d
```

### 📦 **Installation Manuelle**
```bash
# Dépendances Python
pip install -r requirements.txt

# Interface desktop
python3 -m gui.desktop_app

# Interface web simple
python3 simple_web.py

# Interface web complète
python3 -m web.app
```

---

## 🌐 **Interface Utilisateur**

### 🖥️ **Interface Desktop**
- **Configuration répertoires** : Source et sortie
- **Paramètres audio** : Bitrate, sample rate, VBR, loudnorm
- **Modes de traitement** : Phase 1/2/3
- **Progression détaillée** : Fichier actuel, pourcentage, logs
- **Actions rapides** : Lancer, pause, arrêter, ouvrir sortie

### 🌐 **Interface Web**
- **Onglets avancés** : Options de base + paramètres avancés
- **Sliders interactifs** : VBR qualité 1-9, loudnorm complet
- **Monitoring temps réel** : CPU, GPU, RAM, progression
- **Historique** : Conversions précédentes avec détails
- **Téléchargement** : Direct des résultats

---

## 🔗 **Intégration Audiobookshelf**

### ⚙️ **Configuration**
```json
{
  "host": "localhost",
  "port": 13378,
  "username": "votre-username",
  "password": "votre-password",
  "enabled": true,
  "auto_sync": true,
  "library_id": "votre-library-id"
}
```

### 🔄 **Fonctionnalités**
- **Upload automatique** : Métadonnées + fichiers après conversion
- **Synchronisation bidirectionnelle** : Local ↔ distant
- **Gestion des conflits** : Stratégies de résolution
- **Support multi-bibliothèques** : Organisation avancée
- **Retry automatique** : Gestion des erreurs réseau

---

## 🐳 **Docker & Déploiement**

### 📋 **Services Disponibles**
- **Application** : Service principal avec health checks
- **Monitoring** : Prometheus + Grafana (optionnel)
- **Base de données** : PostgreSQL (optionnel)
- **Cache** : Redis pour performances (optionnel)

### 🔧 **Configuration**
```yaml
# docker-compose.yml
services:
  audiobook-manager:
    image: gitea.lamachere.fr/audiobook-manager-pro:latest
    ports:
      - "5000:5000"
    volumes:
      - ./data/source:/app/data/source
      - ./data/output:/app/data/output
    environment:
      - MAX_WORKERS=32
      - CPU_THREADS=16
```

---

## 🧪 **Tests et Qualité**

### 📊 **Suite de Tests**
- **Tests unitaires** : 100% modules core, web, integrations
- **Tests d'intégration** : Audiobookshelf + Docker
- **Tests performance** : Benchmarks et mémoire
- **Tests sécurité** : Scans automatiques

### 🛡️ **Sécurité**
- **Scans automatiques** : Trivy, Bandit, Safety
- **SBOM generation** : Software Bill of Materials
- **Vulnerability detection** : Dépendances et images
- **Code quality** : Flake8, Black, MyPy

---

## Documentation

### Documentation Complète
- Guide installation : [Installation One-Click, Docker, manuel](docs/INSTALLATION.md)
- Configuration CI/CD : Workflows Gitea complets
- API documentation : Endpoints et exemples
- Guide développeur : [Architecture et contribution](docs/DEVELOPER.md)
- Dépannage avancé : Problèmes communs et solutions
- GitHub Repository : https://github.com/Nehwon/audiobook-master
- Issues : https://github.com/Nehwon/audiobook-master/issues

### Liens Utiles
- Documentation : https://docs.audiobook-manager.pro
- GitHub Repository : https://github.com/Nehwon/audiobook-master
- Issues : https://github.com/Nehwon/audiobook-master/issues

---

## Cas d'Usage
## 🎯 **Cas d'Usage**

### 🎧 **Pour les Utilisateurs**
- **Conversion rapide** : Phase 1 pour concaténation 1:1
- **Qualité optimale** : Phase 2 pour encodage AAC adaptatif
- **Traitement batch** : Gestion de dossiers complexes
- **Synchronisation** : Upload automatique vers Audiobookshelf

### 🏢 **Pour les Professionnels**
- **Traitement industriel** : Double Xeon 32 cœurs optimisé
- **Déploiement Docker** : Production et staging
- **Monitoring avancé** : Métriques et alertes
- **Intégration continue** : CI/CD complet

---

## 📈 **Roadmap Future**

### 🚀 **Version 2.2 (En cours)**
- [ ] **Auto-update intégré** : Mises à jour automatiques
- [ ] **Notifications avancées** : Slack/Discord/Email
- [ ] **Performance monitoring** : Métriques production
- [ ] **Rollback avancé** : Gestion des versions

### 🔮 **Vision Long Terme**
- **Interface Electron** : Version desktop moderne
- **Plugin architecture** : Extensibilité maximale
- **Cloud services** : SaaS multi-tenant
- **Mobile apps** : iOS/Android natifs

---

## 🏆 **Réalisations Exceptionnelles**

### ✅ **Version 2.0 - Multithreading CPU Optimisé**
- Performance 3.5x plus rapide que séquentiel
- Double Xeon 32 cœurs : 32 workers parallèles
- Analyse qualité adaptative fichier par fichier
- Interface web avancée avec onglets et sliders

### ✅ **Version 2.1 - Dockerisation & Interface Graphique**
- Dockerisation complète multi-plateforme
- Interface desktop Tkinter moderne
- Intégration Audiobookshelf complète
- CI/CD complet avec build Docker auto
- Installation one-click automatisée

---

## 🎧 **Communauté et Support**

### 💬 **Aide et Support**
- **Documentation complète** : Guides et tutoriels
- **Issues GitHub** : Rapport de bugs et demandes
- **Discord communautaire** : Aide entre utilisateurs
- **Examples et templates** : Cas d'usage courants

### 🤝 **Contribution**
- **Code source ouvert** : MIT License
- **Développement collaboratif** : Pull requests bienvenues
- **Documentation contributive** : Améliorations continues
- **Tests et qualité** : Standards élevés

---

## 📄 **Licence**

**MIT License** - Utilisation libre et open source

---

**Pour commencer rapidement :**

```bash
# Installation one-click
curl -fsSL https://raw.githubusercontent.com/Nehwon/audiobook-master/main/scripts/install.sh | bash

# Ou avec Docker
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master
docker-compose up -d
```

**Profitez dès maintenant du traitement d'audiobooks le plus avancé !** 🎧🚀

---

## 📊 **Tableau de Suivi des Commits**

### 🔄 **Règle de Mise à Jour Obligatoire**

**⚠️ IMPORTANT** : Ce tableau doit être mis à jour **À CHAQUE FOIS** que le README.md est modifié ou demandé en mise à jour. C'est une règle non négociable pour assurer la traçabilité complète des modifications.

### 📋 **Historique des Commits Récents**

| Date | Description du Commit | Commit GitHub | Commit Gitea |
|------|----------------------|---------------|--------------|
| 2026-03-04 | Fix server 500 errors and JSON issues | `993d078` | `993d078` |
| 2026-03-04 | Use GHCR image in compose instead of local build | `767a095` | `767a095` |
| 2026-03-04 | Parametrize docker-compose with defaults and add .env.example | `798e680` | `798e680` |
| 2026-03-04 | Fix rename button functionality | `3f0afcd` | `3f0afcd` |
| 2026-03-04 | Normalize apostrophes for FFmpeg-safe folder renaming | `e006531` | `e006531` |
| 2026-03-04 | Fix smart folder renaming in web UI API | `5adf2d1` | `5adf2d1` |
| 2026-03-04 | Configure Docker image build in GitHub Actions | `55b21db` | `55b21db` |
| 2026-03-04 | Update GUI to match docker-compose.yml | `b2e14fb` | `b2e14fb` |
| 2026-03-04 | Fix nginx access log permission error | `2ae16c4` | `2ae16c4` |
| 2026-03-04 | Fix CLI synopsis disable flag compatibility | `11f56a3` | `11f56a3` |
| 2026-03-04 | Documentation complète v2.1.0 - Mise à jour et nouveaux guides | `c3c46eb` | `c3c46eb` |

### 📈 **Statistiques de Synchronisation**

- **Total commits synchronisés** : 11
- **Dernière synchronisation** : 4 Mars 2026
- **Statut** : ✅ GitHub et Gitea parfaitement synchronisés
- **Prochaine mise à jour requise** : À chaque modification du README.md

### 🔗 **Liens Directs**

- **GitHub Repository** : https://github.com/Nehwon/audiobook-master
- **Gitea Repository** : https://gitea.lamachere.fr/fabrice/audiobooks-master
- **GitHub Actions** : https://github.com/Nehwon/audiobook-master/actions

---

*Dernière mise à jour du tableau : 4 Mars 2026* 📊✨
