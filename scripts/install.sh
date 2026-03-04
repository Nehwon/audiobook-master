#!/bin/bash
# 🚀 Script d'Installation One-Click - Audiobook Manager Pro
# Installation automatique pour Linux/macOS/Windows (via WSL)

set -e

# Couleurs pour le output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions de logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Détection du système
detect_system() {
    log_info "Détection du système..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        SYSTEM="linux"
        INSTALL_CMD="sudo apt-get install -y"
        PACKAGE_MANAGER="apt"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        SYSTEM="macos"
        INSTALL_CMD="brew install"
        PACKAGE_MANAGER="brew"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        SYSTEM="windows"
        INSTALL_CMD="choco install"
        PACKAGE_MANAGER="choco"
    else
        log_error "Système non supporté: $OSTYPE"
        exit 1
    fi
    
    log_success "Système détecté: $SYSTEM"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérification Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        log_error "Python 3.8+ est requis (version actuelle: $PYTHON_VERSION)"
        exit 1
    fi
    
    log_success "Python $PYTHON_VERSION détecté"
    
    # Vérification FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        log_warning "FFmpeg n'est pas installé, installation en cours..."
        install_ffmpeg
    else
        log_success "FFmpeg détecté"
    fi
    
    # Vérification Git
    if ! command -v git &> /dev/null; then
        log_warning "Git n'est pas installé, installation en cours..."
        install_git
    else
        log_success "Git détecté"
    fi
}

# Installation FFmpeg
install_ffmpeg() {
    case $SYSTEM in
        "linux")
            sudo apt-get update
            sudo apt-get install -y ffmpeg
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                log_info "Installation de Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install ffmpeg
            ;;
        "windows")
            if ! command -v choco &> /dev/null; then
                log_info "Installation de Chocolatey..."
                powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
            fi
            choco install ffmpeg
            ;;
    esac
}

# Installation Git
install_git() {
    case $SYSTEM in
        "linux")
            sudo apt-get update
            sudo apt-get install -y git
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                log_info "Installation de Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install git
            ;;
        "windows")
            if ! command -v choco &> /dev/null; then
                log_info "Installation de Chocolatey..."
                powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
            fi
            choco install git
            ;;
    esac
}

# Installation de l'application
install_app() {
    log_info "Installation d'Audiobook Manager Pro..."
    
    # Création du répertoire d'installation
    INSTALL_DIR="$HOME/.audiobook-manager"
    mkdir -p "$INSTALL_DIR"
    
    # Clone du dépôt
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        log_info "Mise à jour du dépôt existant..."
        cd "$INSTALL_DIR"
        git pull origin main
    else
        log_info "Clone du dépôt..."
        git clone https://github.com/fabrice-audiobook/audiobooks-manager.git "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    # Installation des dépendances Python
    log_info "Installation des dépendances Python..."
    python3 -m pip install --user -r requirements.txt
    
    # Création du launcher
    create_launcher
}

# Création du launcher
create_launcher() {
    log_info "Création du launcher..."
    
    case $SYSTEM in
        "linux")
            create_linux_launcher
            ;;
        "macos")
            create_macos_launcher
            ;;
        "windows")
            create_windows_launcher
            ;;
    esac
}

# Launcher Linux
create_linux_launcher() {
    cat > "$HOME/.local/bin/audiobook-manager" << 'EOF'
#!/bin/bash
cd "$HOME/.audiobook-manager"
python3 -m gui.desktop_app
EOF
    
    chmod +x "$HOME/.local/bin/audiobook-manager"
    
    # Ajout au PATH si nécessaire
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        log_info "Ajout au PATH dans ~/.bashrc"
    fi
    
    # Création du fichier desktop
    cat > "$HOME/.local/share/applications/audiobook-manager.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Audiobook Manager Pro
Comment=Système de traitement d'audiobooks avec multithreading CPU optimisé
Exec=$HOME/.local/bin/audiobook-manager
Icon=$HOME/.audiobook-manager/gui/icon.png
Terminal=false
Categories=AudioVideo;Audio;
EOF
}

# Launcher macOS
create_macos_launcher() {
    cat > "$HOME/.audiobook-manager/audiobook-manager.sh" << 'EOF'
#!/bin/bash
cd "$HOME/.audiobook-manager"
python3 -m gui.desktop_app
EOF
    
    chmod +x "$HOME/.audiobook-manager/audiobook-manager.sh"
    
    log_info "Création d'un alias dans ~/.zshrc ou ~/.bash_profile..."
    if [[ -f "$HOME/.zshrc" ]]; then
        echo 'alias audiobook-manager="bash ~/.audiobook-manager/audiobook-manager.sh"' >> "$HOME/.zshrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
        echo 'alias audiobook-manager="bash ~/.audiobook-manager/audiobook-manager.sh"' >> "$HOME/.bash_profile"
    fi
}

# Launcher Windows
create_windows_launcher() {
    cat > "$HOME/audiobook-manager.bat" << 'EOF'
@echo off
cd %USERPROFILE%\.audiobook-manager
python gui\desktop_app.py
EOF
    
    log_info "Création d'un raccourci sur le bureau..."
    if [[ -d "$HOME/Desktop" ]]; then
        cp "$HOME/audiobook-manager.bat" "$HOME/Desktop/"
    fi
}

# Configuration post-installation
post_install() {
    log_info "Configuration post-installation..."
    
    # Création des répertoires par défaut
    mkdir -p "$HOME/Audiobooks" "$HOME/Audiobooks/output" "$HOME/Audiobooks/temp"
    
    # Configuration par défaut
    cat > "$HOME/.audiobook-manager/config.json" << EOF
{
    "source_directory": "$HOME/Audiobooks",
    "output_directory": "$HOME/Audiobooks/output",
    "temp_directory": "$HOME/Audiobooks/temp",
    "processing_mode": "encode_aac",
    "audio_bitrate": "128k",
    "sample_rate": 48000,
    "enable_gpu_acceleration": false,
    "enable_loudnorm": true
}
EOF
    
    log_success "Configuration par défaut créée"
}

# Fonction principale
main() {
    echo "🎧 Audiobook Manager Pro - Installation One-Click"
    echo "=================================================="
    
    detect_system
    check_prerequisites
    install_app
    post_install
    
    echo ""
    log_success "Installation terminée avec succès !"
    echo ""
    log_info "Pour lancer l'application :"
    
    case $SYSTEM in
        "linux")
            echo "  • Via le terminal: audiobook-manager"
            echo "  • Via le menu: Applications > Son et vidéo > Audiobook Manager Pro"
            ;;
        "macos")
            echo "  • Via le terminal: audiobook-manager"
            echo "  • Via Spotlight: cherchez 'Audiobook Manager Pro'"
            ;;
        "windows")
            echo "  • Double-cliquez sur 'audiobook-manager.bat'"
            echo "  • Via le bureau: raccourci Audiobook Manager Pro"
            ;;
    esac
    
    echo ""
    log_info "Répertoire de configuration: $HOME/.audiobook-manager"
    log_info "Documentation: https://github.com/fabrice-audiobook/audiobooks-manager"
    echo ""
    log_success "Profitez bien d'Audiobook Manager Pro ! 🎧"
}

# Gestion des erreurs
trap 'log_error "Installation échouée à l''étape $LINENO"; exit 1' ERR

# Lancement
main "$@"