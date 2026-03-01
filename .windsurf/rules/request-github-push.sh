#!/bin/bash

# Script de demande de confirmation pour push GitHub
# Usage: ./request-github-push.sh [branche] [description]

echo "📋 DEMANDE DE PUSH GITHUB"
echo "=========================="

# Paramètres
branch=${1:-$(git rev-parse --abbrev-ref HEAD)}
description=${2:-"Mise à jour de la branche $branch"}

# Informations
current_date=$(date "+%Y-%m-%d %H:%M:%S")
author=$(git config user.name)
commit_count=$(git rev-list --count origin/$branch..HEAD 2>/dev/null || echo "N/A")

echo "📍 Branche: $branch"
echo "👤 Auteur: $author"
echo "📅 Date: $current_date"
echo "📊 Commits en attente: $commit_count"
echo ""

# Derniers commits
echo "📝 Derniers commits:"
git log --oneline -5 2>/dev/null || echo "Aucun commit trouvé"
echo ""

# Changements
echo "📋 Description:"
echo "$description"
echo ""

# Validation checklist
echo "✅ CHECKLIST DE VALIDATION"
echo "========================"
echo "☐ Tests unitaires passés"
echo "☐ Tests d'intégration passés" 
echo "☐ Performance vérifiée"
echo "☐ Sécurité validée"
echo "☐ Documentation mise à jour"
echo "☐ CHANGELOG.md mis à jour"
echo ""

# Impact
echo "🎯 IMPACT"
echo "=========="
echo "Utilisateurs: ________________________"
echo "Performance: ________________________"
echo "Sécurité: ________________________"
echo ""

# Confirmation
echo "🚨 DEMANDE DE CONFIRMATION"
echo "=========================="
echo "Je confirme avoir validé tous les points ci-dessus"
echo "et autorise le push vers GitHub pour la branche $branch"
echo ""
echo "Signature: ________________________"
echo "Date: ________________________"
echo ""

# Créer le fichier de confirmation
read -p "❓ Créer la demande de confirmation? (oui/non): " create_request

if [[ "$create_request" == "oui" ]]; then
    # Créer le fichier de demande
    request_file=".github_push_request_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$request_file" << EOF
# Demande de Push GitHub

**Branche**: $branch
**Auteur**: $author
**Date**: $current_date
**Commits en attente**: $commit_count

## 📋 Changements
$description

## 📝 Derniers commits
\`\`\`
$(git log --oneline -5 2>/dev/null || echo "Aucun commit trouvé")
\`\`\`

## ✅ Checklist de Validation
- [ ] Tests unitaires passés
- [ ] Tests d'intégration passés
- [ ] Performance vérifiée
- [ ] Sécurité validée
- [ ] Documentation mise à jour
- [ ] CHANGELOG.md mis à jour

## 🎯 Impact
- **Utilisateurs**: ________________________
- **Performance**: ________________________
- **Sécurité**: ________________________

## 🚨 Demande de Confirmation
Je confirme avoir validé tous les points ci-dessus et autorise le push vers GitHub.

**Signature**: ________________________
**Date**: ________________________
EOF

    echo "✅ Demande créée: $request_file"
    echo ""
    echo "📝 Prochaines étapes:"
    echo "1. Compléter la demande dans: $request_file"
    echo "2. Faire valider par l'auteur (Fabrice)"
    echo "3. Créer le fichier .github_push_confirmed"
    echo "4. Lancer le push: git push github $branch"
else
    echo "❌ Demande annulée"
fi
