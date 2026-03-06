# 🎧 Audiobook Manager Pro

Système professionnel de traitement d'audiobooks avec multithreading CPU optimisé, interface graphique desktop et synchronisation Audiobookshelf.

## 🚀 **Version 2.1.0 - Dockerisation & Interface Graphique & Synchronisation**

### ✅ **Nouvelles Fonctionnalités Majeures**

#### 🐳 **Dockerisation Complète**
- **Dockerfile** : Configuration complète avec FFmpeg 7.1.3 et dépendances
- **Docker Compose** : Services (app, Ollama, monitoring, BDD, Redis) avec paramètres `.env`
- **Multi-plateforme** : Support Linux/Windows/macOS
- **Health checks** : Endpoints `/health` et `/api/status`
- **Installation one-click** : Script automatisé multi-OS
- **Interface web simple** : `simple_web.py` pour monitoring basique
- **Registry GHCR** : Images GitHub Container Registry intégrées
- **Workflow GitHub Actions** : Build Docker automatisé

#### 🖥️ **Interface Web Avancée**
- **Application Flask moderne** : Interface responsive avec SocketIO
- **Progression dynamique** : Barres de progression temps réel par job
- **Notifications système** : Remplacement des popups par notifications élégantes
- **Renommage intelligent** : Édition manuelle des titres avec assistance Ollama
- **Logs détaillés** : Tracking live des traitements avec debug complet
- **Indicateur busy global** : État de l'application visible en permanence
- **Recherche IA intégrée** : Ollama pour analyse et suggestions de métadonnées

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
- **Validation robuste** : Rejet des dossiers contenant des sous-dossiers
- **Diagnostics avancés** : Logs persistants dans `/app/logs` avec analyse d'échecs

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

# Stack all-in-one (app + Ollama)
docker-compose up -d
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
- **LLM local** : Ollama embarqué pour le scraping/extraction métadonnées

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
| 2026-03-06 | Remove audiobook buttons during conversion + dynamic job bars | `9c8ec77` | `9c8ec77` |
| 2026-03-06 | Expose conversion progress to API and render dynamic job bars | `8f9aca2` | `8f9aca2` |
| 2026-03-06 | Fix FFmpeg error on audio processing + reject subdirectories | `53267b3` | `53267b3` |
| 2026-03-06 | Reject audiobook folders that contain subdirectories | `841dc6f` | `841dc6f` |
| 2026-03-06 | Fix log file not found error + persist processor logs | `4d5d9a2` | `4d5d9a2` |
| 2026-03-06 | Persist processor logs in /app/logs and improve failure diagnostics | `6b3dac7` | `6b3dac7` |
| 2026-03-06 | Fix web debug log location to use /app/logs | `3ce04b6` | `3ce04b6` |
| 2026-03-06 | Fix backend logs API error 504 + jobs lock deadlock | `bd3929b` | `bd3929b` |
| 2026-03-06 | Fix web jobs lock deadlock blocking logs and status APIs | `c95cbbe` | `c95cbbe` |
| 2026-03-06 | Add detailed web processing logs and live tracking UI | `d8f922b` | `d8f922b` |
| 2026-03-06 | Refactor rename functionality and replace popups by notifications | `1eabcff` | `1eabcff` |
| 2026-03-06 | Améliore le renommage manuel et remplace les popups par notifications | `d473558` | `d473558` |
| 2026-03-06 | Allow user to edit title manually + Ollama assisted renaming | `80ee814` | `80ee814` |
| 2026-03-06 | Ajouter bouton titre manuel et renommage assisté par Ollama | `42072d8` | `42072d8` |
| 2026-03-06 | Fix failed API calls in GUI for Ollama search and model pull | `a66bf0e` | `a66bf0e` |
| 2026-03-06 | Fix Ollama UI failures for search and model pull | `1475f40` | `1475f40` |
| 2026-03-06 | Add global busy indicator and model pull progress bar | `aecb0fd` | `aecb0fd` |

### 📈 **Statistiques de Synchronisation**

- **Total commits synchronisés** : 17
- **Dernière synchronisation** : 6 Mars 2026
- **Statut** : ✅ GitHub et Gitea parfaitement synchronisés
- **Prochaine mise à jour requise** : À chaque modification du README.md

### 🔗 **Liens Directs**

- **GitHub Repository** : https://github.com/Nehwon/audiobook-master
- **Gitea Repository** : https://gitea.lamachere.fr/fabrice/audiobooks-master
- **GitHub Actions** : https://github.com/Nehwon/audiobook-master/actions

---

*Dernière mise à jour du tableau : 6 Mars 2026* 📊✨
