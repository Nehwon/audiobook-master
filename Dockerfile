# 🐳 Dockerfile - Audiobook Manager Pro
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="fabrice@audiobook-manager.pro"
LABEL description="Système de traitement d'audiobooks avec multithreading CPU optimisé"
LABEL version="2.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    unrar-free \
    p7zip-full \
    libarchive-tools \
    libavcodec-extra \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    libswresample-dev \
    libavfilter-dev \
    pkg-config \
    curl \
    wget \
    git \
    build-essential \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Création de l'utilisateur audiobook
RUN groupadd -r audiobook && useradd -r -g audiobook -d /app -s /bin/bash audiobook

# Configuration du répertoire de travail
WORKDIR /app

# Copie des fichiers requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn psutil

# Copie du code source
COPY . .

# Configuration des permissions
RUN chown -R audiobook:audiobook /app && \
    if [ -f /app/run.py ]; then chmod +x /app/run.py; fi

# Création des répertoires nécessaires
RUN mkdir -p /app/logs /app/temp /app/data && \
    chown -R audiobook:audiobook /app/logs /app/temp /app/data

# Volume pour les données
VOLUME ["/app/data", "/app/logs", "/app/temp"]

# Port d'écoute
EXPOSE 8080

# Variables d'environnement par défaut
ENV FLASK_APP=web/app.py \
    FLASK_ENV=production \
    GUNICORN_WORKERS=1 \
    GUNICORN_THREADS=8 \
    GUNICORN_TIMEOUT=300

# Script de démarrage
COPY docker-entrypoint.sh /usr/local/bin/
COPY deploy/nginx.conf /etc/nginx/nginx.conf
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Exécution en root pour faciliter les tests locaux avec volumes bind mount
USER root

# Point d'entrée
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["web"]
