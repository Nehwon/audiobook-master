#!/bin/bash

# Hook Git pour contrôler les pushes GitHub
# Placez ce fichier dans .git/hooks/pre-push

echo "🔒 Vérification des règles de push GitHub..."

# Récupérer le remote destination
remote_name=$1
remote_url=$2

# Vérifier si c'est un push vers GitHub
if [[ "$remote_url" == *"github.com"* ]]; then
    echo "🚨 DÉTECTION DE PUSH VERS GITHUB"
    
    # Vérifier si confirmation existe
    if [ ! -f ".github_push_confirmed" ]; then
        echo "❌ ERREUR: Push GitHub non autorisé sans confirmation!"
        echo ""
        echo "📋 Processus à suivre:"
        echo "1. Créer une demande de confirmation"
        echo "2. Attendre validation de l'auteur (Fabrice)"
        echo "3. Créer le fichier .github_push_confirmed"
        echo "4. Relancer le push"
        echo ""
        echo "📝 Template de demande disponible dans .windsurf/rules/git-workflow.md"
        exit 1
    fi
    
    # Vérifier la branche actuelle
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    echo "📍 Branche actuelle: $current_branch"
    
    # Autoriser uniquement main et dev pour GitHub
    if [[ "$current_branch" != "main" && "$current_branch" != "dev" ]]; then
        echo "❌ ERREUR: Push GitHub uniquement autorisé depuis main ou dev"
        echo "   Branche actuelle: $current_branch"
        exit 1
    fi
    
    # Vérifier les tests si disponible
    if [ -d "tests" ]; then
        echo "🧪 Vérification des tests..."
        if ! python -m pytest tests/ --quiet; then
            echo "❌ ERREUR: Tests en échec - Push GitHub interdit"
            exit 1
        fi
        echo "✅ Tests validés"
    fi
    
    # Vérifier la documentation
    echo "📚 Vérification de la documentation..."
    if [ ! -f "README.md" ]; then
        echo "❌ ERREUR: README.md manquant - Push GitHub interdit"
        exit 1
    fi
    
    if [ ! -f "CHANGELOG.md" ]; then
        echo "❌ ERREUR: CHANGELOG.md manquant - Push GitHub interdit"
        exit 1
    fi
    
    echo "✅ Documentation validée"
    
    # Demander confirmation finale
    echo "🚨 PUSH VERS GITHUB DÉTECTÉ"
    echo "📋 Branche: $current_branch"
    echo "📁 Remote: $remote_name"
    echo ""
    read -p "❓ Confirmer le push vers GitHub? (oui/non): " confirmation
    
    if [[ "$confirmation" != "oui" ]]; then
        echo "❌ Push GitHub annulé"
        exit 1
    fi
    
    # Nettoyer le fichier de confirmation
    rm -f .github_push_confirmed
    echo "✅ Push GitHub autorisé"
else
    echo "✅ Push vers Gitea autorisé"
fi

exit 0
