# 🐳 Docker Configuration - Audiobook Manager Pro

## 📋 Prérequis

- **Docker** 20.10+ et **Docker Compose** 2.0+
- **Docker** avec accès aux ressources CPU (important pour le multithreading)
- **Espace disque** : 10GB+ pour les conteneurs et volumes
- **RAM** : 4GB+ recommandé pour les traitements

---

## 🚀 Installation Rapide

### 1. **Cloner le dépôt**
```bash
git clone https://github.com/fabrice-audiobook/audiobooks-manager.git
cd audiobooks-manager
```

### 2. **Configuration des volumes**
```bash
# Créer les répertoires de données
mkdir -p data/{source,output,temp} logs

# Donner les permissions appropriées
chmod 755 data/{source,output,temp} logs
```

### 3. **Démarrage rapide**
```bash
# Démarrer uniquement l'application web
docker-compose up -d

# Ou avec monitoring inclus
docker-compose --profile monitoring up -d

# Ou avec tous les services
docker-compose --profile monitoring --profile database --profile cache up -d
```

---

## ⚙️ Configuration

### 🌁 Variables d'Environnement

Créer un fichier `.env` pour personnaliser la configuration :

```bash
# 🌐 Configuration Web
HOST=0.0.0.0
PORT=5000
FLASK_ENV=production

# 📁 Répertoires
SOURCE_DIR=/app/data/source
OUTPUT_DIR=/app/data/output
TEMP_DIR=/app/temp

# 🚀 Performance (adapter selon votre système)
GUNICORN_WORKERS=4
GUNICORN_THREADS=8
GUNICORN_TIMEOUT=300

# 🖥️ Configuration CPU (double Xeon 32 cœurs)
MAX_WORKERS=32
CPU_THREADS=16
BATCH_THREADS=8

# 📊 Logging
LOG_LEVEL=INFO
```

### 🎯 Optimisation CPU

Pour un double Xeon 32 cœurs, utilisez cette configuration :

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  audiobook-manager:
    deploy:
      resources:
        limits:
          cpus: '32'        # Utiliser tous les cœurs logiques
          memory: 16G        # Adapter selon votre RAM
        reservations:
          cpus: '16'
          memory: 4G
    environment:
      - MAX_WORKERS=32
      - CPU_THREADS=16
      - BATCH_THREADS=8
      - GUNICORN_WORKERS=8
      - GUNICORN_THREADS=16
```

---

## 📊 Services Optionnels

### 🔍 Monitoring Stack

Activez le monitoring complet :

```bash
# Démarrer avec Prometheus + Grafana
docker-compose --profile monitoring up -d

# Accès aux services:
# - Application: http://localhost:5000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin123)
```

### 🗄️ Base de Données

Pour les fonctionnalités avancées nécessitant une base de données :

```bash
# Démarrer avec PostgreSQL
docker-compose --profile database up -d

# Configuration de la base:
# - Host: localhost:5432
# - Database: audiobook_manager
# - User: audiobook
# - Password: audiobook123
```

### 🔄 Cache Redis

Pour améliorer les performances avec Redis :

```bash
# Démarrer avec Redis
docker-compose --profile cache up -d

# Configuration Redis:
# - Host: localhost:6379
# - Max memory: 512MB
```

---

## 🛠️ Commandes Utiles

### 📋 Gestion des Conteneurs

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Redémarrer un service
docker-compose restart audiobook-manager

# Voir les logs
docker-compose logs -f audiobook-manager

# Voir les ressources utilisées
docker stats audiobook-manager
```

### 🔄 Mise à Jour

```bash
# Mettre à jour l'application
git pull
docker-compose build --no-cache
docker-compose up -d

# Nettoyer les anciennes images
docker image prune -f
```

### 📁 Gestion des Données

```bash
# Sauvegarder les données
docker run --rm -v audiobooks-manager_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .

# Restaurer les données
docker run --rm -v audiobooks-manager_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /data
```

---

## 🔧 Dépannage

### 🚨 Problèmes Communs

#### **Problème de permissions**
```bash
# Corriger les permissions des volumes
sudo chown -R 1000:1000 data/ logs/
```

#### **Problème de performance CPU**
```bash
# Vérifier que Docker a accès aux CPU
docker run --rm alpine nproc
# Devrait retourner 32+ pour un double Xeon

# Limiter les ressources si nécessaire
docker-compose up -d --scale audiobook-manager=1
```

#### **Problème de mémoire**
```bash
# Augmenter la mémoire swap si nécessaire
sudo swapon --show
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 📊 Monitoring

```bash
# Voir les ressources en temps réel
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Voir les logs d'erreur
docker-compose logs audiobook-manager | grep ERROR

# Accéder au conteneur pour debug
docker-compose exec audiobook-manager bash
```

---

## 🎯 Production

### 🔒 Sécurité

Pour un environnement de production :

```bash
# Utiliser des secrets Docker
echo "audiobook123" | docker secret create db_password -

# Utiliser un reverse proxy (nginx/traefik)
# Ne pas exposer directement le port 5000
```

### 📈 Scalabilité

```bash
# Scaler horizontalement (si nécessaire)
docker-compose up -d --scale audiobook-manager=2

# Utiliser Docker Swarm ou Kubernetes pour le clustering
```

---

## 📚 Documentation Complète

- **Documentation API** : http://localhost:5000/docs
- **Monitoring Grafana** : http://localhost:3000
- **Métriques Prometheus** : http://localhost:9090

---

*Pour le support technique, consultez le [GitHub Repository](https://github.com/fabrice-audiobook/audiobooks-manager/issues)*