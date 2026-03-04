# 🚀 Guide d'Installation - Audiobook Manager Pro

Guide complet d'installation pour toutes les plateformes et méthodes.

---

## 📋 **Prérequis Système**

### **Configuration Minimale**
- **OS** : Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Python** : 3.8+ (recommandé 3.11)
- **RAM** : 4GB minimum (8GB+ recommandé)
- **CPU** : 2 cœurs minimum (4+ recommandé)
- **Stockage** : 10GB libre (50GB+ recommandé)

### **Configuration Optimale**
- **OS** : Linux (Ubuntu 22.04 LTS)
- **Python** : 3.11+
- **RAM** : 16GB+
- **CPU** : 8+ cœurs (16+ recommandé)
- **Stockage** : SSD NVMe 100GB+
- **Réseau** : 1Gbps+ pour synchronisation cloud

---

## 🚀 **Méthode 1: Installation One-Click (Recommandée)**

### **Linux/macOS**
```bash
# Téléchargement et installation automatique
curl -fsSL https://raw.githubusercontent.com/Nehwon/audiobook-master/main/scripts/install.sh | bash

# Ou avec wget
wget -qO- https://raw.githubusercontent.com/Nehwon/audiobook-master/main/scripts/install.sh | bash
```

### **Windows (PowerShell)**
```powershell
# Téléchargement et exécution
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Nehwon/audiobook-master/main/scripts/install.ps1" -OutFile "install.ps1"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install.ps1
```

### **Ce que fait l'installation one-click**
- ✅ **Détection OS** et architecture
- ✅ **Installation Python** si nécessaire
- ✅ **Installation FFmpeg** avec tous les codecs
- ✅ **Création répertoires** utilisateur
- ✅ **Configuration variables** d'environnement
- ✅ **Installation dépendances** Python
- ✅ **Raccourcis système** et menu démarrer
- ✅ **Vérification post-installation**

---

## 🐳 **Méthode 2: Docker (Production)**

### **Prérequis Docker**
```bash
# Installation Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **Installation avec Docker Hub**
```bash
# Pull image officielle
docker pull nehwon/audiobook-manager-pro:latest

# Lancement simple
docker run -d \
  --name audiobook-manager \
  -p 5000:5000 \
  -v /path/to/audiobooks:/app/data/source \
  -v /path/to/output:/app/data/output \
  nehwon/audiobook-manager-pro:latest
```

### **Installation depuis Source**
```bash
# Clone repository
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master

# Build image
docker build -t audiobook-manager-pro:v2.1.0 .

# Lancement avec Docker Compose
docker-compose up -d

# Avec monitoring
docker-compose --profile monitoring up -d
```

### **Configuration Docker**
```yaml
# docker-compose.yml
version: '3.8'
services:
  audiobook-manager:
    image: audiobook-manager-pro:v2.1.0
    container_name: audiobook-manager
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./data/source:/app/data/source:ro
      - ./data/output:/app/data/output:rw
      - ./data/temp:/app/temp:rw
      - ./logs:/app/logs:rw
    environment:
      - MAX_WORKERS=16
      - CPU_THREADS=8
      - LOG_LEVEL=INFO
      - AUDIOBOOKSHELF_ENABLED=true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 📦 **Méthode 3: Installation Manuelle**

### **Installation Python**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# CentOS/RHEL
sudo dnf install python3.11 python3.11-pip

# macOS (Homebrew)
brew install python@3.11

# Windows (Chocolatey)
choco install python
```

### **Installation FFmpeg**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg libavcodec-extra

# CentOS/RHEL
sudo dnf install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

### **Installation Dépendances**
```bash
# Clone repository
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master

# Création environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou venv\Scripts\activate  # Windows

# Installation dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Installation dépendances développement (optionnel)
pip install -r requirements_test.txt
```

---

## 🖥️ **Lancement Applications**

### **Interface Desktop**
```bash
# Interface desktop Tkinter
python3 -m gui.desktop_app

# Ou directement
python3 gui/desktop_app.py
```

### **Interface Web Simple**
```bash
# Interface web monitoring basique
python3 simple_web.py

# Accès : http://localhost:5000
```

### **Interface Web Complète**
```bash
# Interface web Flask complète
python3 -m web.app

# Ou avec Gunicorn (production)
gunicorn --workers 4 --bind 0.0.0.0:5000 web.app:app
```

### **Interface Ligne de Commande**
```bash
# Traitement direct
python3 -m core.main --source /path/to/audiobooks --output /path/to/output

# Avec configuration
python3 -m core.main --config config.json

# Aide
python3 -m core.main --help
```

---

## ⚙️ **Configuration Post-Installation**

### **Variables d'Environnement**
```bash
# Ajouter au ~/.bashrc ou ~/.zshrc
export AUDIOBOOK_SOURCE_DIR="$HOME/Audiobooks"
export AUDIOBOOK_OUTPUT_DIR="$HOME/Audiobooks_Processed"
export AUDIOBOOK_TEMP_DIR="/tmp/audiobooks_web"
export MAX_WORKERS=8
export CPU_THREADS=4
export LOG_LEVEL=INFO

# Recharger shell
source ~/.bashrc
```

### **Fichier Configuration**
```bash
# Créer configuration
mkdir -p ~/.config/audiobook-manager
cp config.example.json ~/.config/audiobook-manager/config.json

# Éditer configuration
nano ~/.config/audiobook-manager/config.json
```

### **Configuration Audiobookshelf**
```json
{
  "audiobookshelf": {
    "host": "localhost",
    "port": 13378,
    "username": "votre-username",
    "password": "votre-password",
    "enabled": true,
    "auto_sync": true,
    "library_id": "votre-library-id",
    "conflict_strategy": "overwrite"
  }
}
```

---

## 🔧 **Vérification Installation**

### **Test Dépendances**
```bash
# Vérifier Python
python3 --version
pip list | grep -E "(flask|mutagen|requests)"

# Vérifier FFmpeg
ffmpeg -version
ffmpeg -codecs | grep mp3
```

### **Test Applications**
```bash
# Test interface desktop
python3 -c "import gui.desktop_app; print('Desktop OK')"

# Test interface web
python3 -c "import web.app; print('Web OK')"

# Test traitement
python3 -c "import core.processor; print('Processor OK')"
```

### **Test Endpoints**
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test API status
curl http://localhost:5000/api/status

# Test conversion (exemple)
curl -X POST http://localhost:5000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"source": "/path/to/audiobook", "output": "/path/to/output"}'
```

---

## 🐛 **Dépannage Installation**

### **Problèmes Communs**

#### **Python non trouvé**
```bash
# Solution : Installer Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv

# Ou utiliser pyenv
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

#### **FFmpeg non trouvé**
```bash
# Solution : Installer FFmpeg complet
sudo apt install ffmpeg libavcodec-extra libavformat-dev

# Ou télécharger binaire officiel
wget https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz
tar -xvf ffmpeg-git-amd64-static.tar.xz
sudo cp ffmpeg-git-*-amd64-static/ffmpeg /usr/local/bin/
```

#### **Permissions refusées**
```bash
# Solution : Corriger permissions
sudo chown -R $USER:$USER ~/.config/audiobook-manager
chmod +x scripts/install.sh

# Pour Docker
sudo usermod -aG docker $USER
newgrp docker
```

#### **Port déjà utilisé**
```bash
# Solution : Changer port ou arrêter service
sudo netstat -tlnp | grep :5000

# Changer port dans docker-compose.yml
ports:
  - "5001:5000"  # Utiliser port 5001
```

### **Logs et Debug**
```bash
# Logs application
tail -f ~/.config/audiobook-manager/logs/audiobook.log

# Logs Docker
docker-compose logs audiobook-manager -f

# Mode debug
export LOG_LEVEL=DEBUG
python3 -m gui.desktop_app
```

---

## 🔄 **Mise à Jour**

### **Mise à Jour Automatique**
```bash
# Script de mise à jour
curl -fsSL https://raw.githubusercontent.com/Nehwon/audiobook-master/scripts/update.sh | bash

# Ou avec l'application
python3 -m gui.desktop_app --update
```

### **Mise à Jour Manuelle**
```bash
# Mettre à jour repository
git pull origin main

# Mettre à jour dépendances
pip install -r requirements.txt --upgrade

# Rebuild Docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 **Support Installation**

### **Obtenir de l'Aide**
- **Documentation** : https://docs.audiobook-manager.pro/installation
- **Issues GitHub** : https://github.com/Nehwon/audiobook-master/issues
- **Discord** : https://discord.gg/audiobook-manager
- **Email** : support@audiobook-manager.pro

### **Rapporter Problème d'Installation**
1. **Vérifier** prérequis système
2. **Consulter** section dépannage
3. **Créer issue** avec template bug-installation
4. **Inclure** : OS, version Python, logs, erreur complète

---

## 🎯 **Prochaines Étapes**

1. **Lancer application** : `python3 -m gui.desktop_app`
2. **Configurer répertoires** : Source et sortie
3. **Paramétrer Audiobookshelf** : Si souhaité
4. **Tester conversion** : Avec petit fichier audio
5. **Explorer documentation** : Pour fonctionnalités avancées

---

*Guide d'installation maintenue activement • Dernière mise à jour : 4 Mars 2026* 🚀✨

*Pour une installation rapide, utilisez la méthode one-click recommandée*
