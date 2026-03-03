#!/bin/bash
# 🐳 Docker Entrypoint - Audiobook Manager Pro

set -e

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Vérification des variables d'environnement
check_env() {
    log "🔍 Vérification des variables d'environnement..."
    
    # Variables requises avec valeurs par défaut
    export SOURCE_DIR=${SOURCE_DIR:-"/app/data/source"}
    export OUTPUT_DIR=${OUTPUT_DIR:-"/app/data/output"}
    export TEMP_DIR=${TEMP_DIR:-"/app/temp"}
    export LOG_LEVEL=${LOG_LEVEL:-"INFO"}
    export HOST=${HOST:-"0.0.0.0"}
    export PORT=${PORT:-"5000"}
    
    log "✅ Variables configurées:"
    log "   SOURCE_DIR: $SOURCE_DIR"
    log "   OUTPUT_DIR: $OUTPUT_DIR"
    log "   TEMP_DIR: $TEMP_DIR"
    log "   LOG_LEVEL: $LOG_LEVEL"
    log "   HOST: $HOST"
    log "   PORT: $PORT"
}

# Création des répertoires
create_directories() {
    log "📁 Création des répertoires..."
    mkdir -p "$SOURCE_DIR" "$OUTPUT_DIR" "$TEMP_DIR"
    log "✅ Répertoires créés"
}

# Vérification de FFmpeg
check_ffmpeg() {
    log "🎵 Vérification de FFmpeg..."
    if ! command -v ffmpeg &> /dev/null; then
        log "❌ FFmpeg non trouvé!"
        exit 1
    fi
    
    ffmpeg_version=$(ffmpeg -version | head -n 1)
    log "✅ FFmpeg détecté: $ffmpeg_version"
}

# Vérification des dépendances Python
check_python_deps() {
    log "🐍 Vérification des dépendances Python..."
    python -c "
import sys
try:
    import flask
    import mutagen
    import requests
    import pydub
    print('✅ Toutes les dépendances Python sont installées')
except ImportError as e:
    print(f'❌ Dépendance manquante: {e}')
    sys.exit(1)
"
}

# Initialisation de la base de données (si nécessaire)
init_database() {
    log "🗄️ Initialisation de la base de données..."
    # Ajouter ici l'initialisation si nécessaire
    log "✅ Base de données prête"
}

# Fonction de démarrage web
start_web() {
    log "🌐 Démarrage de l'interface web..."
    log "🚀 Lancement de Gunicorn sur $HOST:$PORT"
    
    exec gunicorn \
        --bind "$HOST:$PORT" \
        --workers "$GUNICORN_WORKERS" \
        --threads "$GUNICORN_THREADS" \
        --timeout "$GUNICORN_TIMEOUT" \
        --access-logfile "/app/logs/access.log" \
        --error-logfile "/app/logs/error.log" \
        --log-level "$LOG_LEVEL" \
        --name audiobook-manager \
        "web.app:app"
}

# Fonction de démarrage CLI
start_cli() {
    log "💻 Démarrage en mode CLI..."
    exec python -m core.main "$@"
}

# Fonction d'aide
show_help() {
    log "📖 Audiobook Manager Pro - Docker Help"
    log ""
    log "Usage: docker-entrypoint.sh [COMMAND] [OPTIONS]"
    log ""
    log "Commands:"
    log "  web              Démarrer l'interface web (défaut)"
    log "  cli              Démarrer en mode CLI"
    log "  help             Afficher cette aide"
    log ""
    log "Environment Variables:"
    log "  SOURCE_DIR       Répertoire des fichiers source"
    log "  OUTPUT_DIR      Répertoire des fichiers de sortie"
    log "  TEMP_DIR        Répertoire temporaire"
    log "  LOG_LEVEL       Niveau de log (DEBUG, INFO, WARNING, ERROR)"
    log "  HOST            Hôte d'écoute (défaut: 0.0.0.0)"
    log "  PORT            Port d'écoute (défaut: 5000)"
    log "  GUNICORN_WORKERS Nombre de workers Gunicorn (défaut: 4)"
    log "  GUNICORN_THREADS  Nombre de threads par worker (défaut: 8)"
    log "  GUNICORN_TIMEOUT Timeout en secondes (défaut: 300)"
}

# Point d'entrée principal
main() {
    log "🎧 Démarrage d'Audiobook Manager Pro v2.0.0"
    
    # Vérifications initiales
    check_env
    create_directories
    check_ffmpeg
    check_python_deps
    init_database
    
    # Traitement de la commande
    case "${1:-web}" in
        "web")
            start_web
            ;;
        "cli")
            shift
            start_cli "$@"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log "❌ Commande inconnue: $1"
            show_help
            exit 1
            ;;
    esac
}

# Gestion du signal SIGTERM pour arrêt gracieux
trap 'log "🛑 Arrêt du conteneur..."; exit 0' SIGTERM

# Lancement
main "$@"