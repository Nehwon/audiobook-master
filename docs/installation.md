# 📦 Installation One-Click - Audiobook Manager Pro

## 🚀 Installation Automatisée

### 🎯 **Installation Rapide**

#### **Linux/macOS**
```bash
# Télécharger et lancer l'installation
curl -fsSL https://raw.githubusercontent.com/fabrice-audiobook/audiobooks-manager/main/scripts/install.sh | bash
```

#### **Windows**
```powershell
# Télécharger et lancer l'installation (PowerShell)
iwr -useb https://raw.githubusercontent.com/fabrice-audiobook/audiobooks-manager/main/scripts/install.sh | iex
```

---

## 📋 **Prérequis Automatiques**

L'installateur vérifie et installe automatiquement :

- ✅ **Python 3.8+** (requis)
- ✅ **FFmpeg** (traitement audio)
- ✅ **Git** (gestionnaire de version)
- ✅ **Dépendances Python** (via pip)

---

## 🖥️ **Post-Installation**

### **Lancement de l'Application**

#### **Linux**
- **Terminal** : `audiobook-manager`
- **Menu** : Applications > Son et vidéo > Audiobook Manager Pro

#### **macOS**
- **Terminal** : `audiobook-manager`
- **Spotlight** : Cherchez "Audiobook Manager Pro"

#### **Windows**
- **Double-cliquez** sur `audiobook-manager.bat`
- **Bureau** : Raccourci Audiobook Manager Pro

### **Configuration**

- **Répertoires par défaut** :
  - Source : `~/Audiobooks`
  - Sortie : `~/Audiobooks/output`
  - Temp : `~/Audiobooks/temp`

- **Fichier de configuration** : `~/.audiobook-manager/config.json`

---

## 🐳 **Installation Docker**

### **Docker Compose (Recommandé)**
```bash
# Clone du dépôt
git clone https://github.com/fabrice-audiobook/audiobooks-manager.git
cd audiobooks-manager

# Démarrage avec Docker Compose
docker-compose up -d

# Avec monitoring inclus
docker-compose --profile monitoring up -d
```

### **Dockerfile Manuel**
```bash
# Construction de l'image
docker build -t audiobook-manager-pro .

# Lancement du conteneur
docker run -d \
  --name audiobook-manager \
  -p 5000:5000 \
  -v $(pwd)/data/source:/app/data/source \
  -v $(pwd)/data/output:/app/data/output \
  audiobook-manager-pro
```

---

## 📦 **Installation Manuelle**

### **Étape 1 : Cloner le Dépôt**
```bash
git clone https://github.com/fabrice-audiobook/audiobooks-manager.git
cd audiobooks-manager
```

### **Étape 2 : Installation Dépendances**
```bash
# Python 3.8+
python3 -m pip install -r requirements.txt

# FFmpeg (Linux/macOS)
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg           # macOS

# FFmpeg (Windows)
# Télécharger depuis https://ffmpeg.org/download.html
```

### **Étape 3 : Lancement**
```bash
# Interface Web
python3 -m web.app

# Interface Desktop
python3 -m gui.desktop_app

# Ligne de Commande
python3 -m core.main --single "Mon Audiobook"
```

---

## 🔧 **Configuration Avancée**

### **Variables d'Environnement**
```bash
# Configuration Audiobookshelf
export AUDIOBOOKSHELF_HOST="localhost"
export AUDIOBOOKSHELF_PORT="13378"
export AUDIOBOOKSHELF_USERNAME="votre-username"
export AUDIOBOOKSHELF_PASSWORD="votre-password"

# Configuration Synchronisation
export SYNC_ENABLED="true"
export SYNC_LIBRARY_ID="votre-library-id"
export SYNC_AUTO="true"
```

### **Fichier de Configuration**
```json
{
  "source_directory": "/path/to/source",
  "output_directory": "/path/to/output",
  "processing_mode": "encode_aac",
  "audio_bitrate": "128k",
  "sample_rate": 48000,
  "enable_gpu_acceleration": false,
  "enable_loudnorm": true,
  "max_workers": 32,
  "cpu_threads": 16
}
```

---

## 🚨 **Dépannage**

### **Problèmes Communs**

#### **Python non trouvé**
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install python3 python3-pip

# macOS
brew install python3

# Windows
# Télécharger depuis python.org
```

#### **FFmpeg non trouvé**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Télécharger depuis ffmpeg.org
```

#### **Permissions refusées**
```bash
# Linux/macOS
chmod +x scripts/install.sh

# Windows
# Exécuter PowerShell en tant qu'Administrateur
```

#### **Port déjà utilisé**
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :5000

# Changer le port
export PORT=5001
python3 -m web.app
```

### **Logs et Debug**

#### **Logs de l'Application**
```bash
# Linux/macOS
tail -f ~/.audiobook-manager/logs/app.log

# Windows
type %USERPROFILE%\.audiobook-manager\logs\app.log
```

#### **Mode Debug**
```bash
# Activer le mode debug
export LOG_LEVEL=DEBUG
python3 -m web.app
```

---

## 📚 **Documentation Complète**

- **Documentation API** : http://localhost:5000/docs
- **Guide Utilisateur** : [README.md](../README.md)
- **Configuration Docker** : [docs/docker-setup.md](../docs/docker-setup.md)
- **Issues GitHub** : https://github.com/fabrice-audiobook/audiobooks-manager/issues

---

## 🆘 **Support**

### **Communauté**
- **Discord** : https://discord.gg/audiobook-manager
- **GitHub Discussions** : https://github.com/fabrice-audiobook/audiobooks-manager/discussions

### **Rapport de Bugs**
- **GitHub Issues** : https://github.com/fabrice-audiobook/audiobooks-manager/issues
- **Logs requis** : Joignez les logs de l'application

---

## 🎯 **Prochaines Étapes**

1. **Configurer** vos répertoires source et sortie
2. **Lancer** votre premier traitement
3. **Explorer** les options avancées (VBR, Loudnorm)
4. **Configurer** la synchronisation Audiobookshelf (optionnel)
5. **Profiter** du traitement ultra-rapide !

---

*Pour une installation personnalisée, consultez le [Guide d'Installation Avancé](../docs/advanced-installation.md)*