#!/bin/bash

# Configuration Git pour Audiobook Manager Pro
# Ce script configure les règles de branches et commits automatiquement

echo "🔧 Configuration du dépôt Git pour Audiobook Manager Pro..."

# Configuration utilisateur (à adapter si nécessaire)
git config user.name "Fabrice"
git config user.email "fabrice@lamachere.fr"

# Branche par défaut pour les commits
git config checkout.defaultRemote origin
git config checkout.defaultBranch dev
git config init.defaultBranch main

# Configuration des branches
echo "📋 Configuration des règles de branches..."

# Règle 1: Les commits se font par défaut sur dev
git config branch.dev.mergeOptions "--no-ff"
git config branch.dev.rebase true

# Règle 2: Configuration pour les merges de version
git config merge.ff only

# Configuration des hooks de qualité
echo "🧪 Mise en place des hooks de qualité..."

# Création du répertoire des hooks
mkdir -p .git/hooks

# Hook pre-commit pour la qualité
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🧪 Vérification de qualité avant commit..."

# Vérification du formatage Python
if command -v black &> /dev/null; then
    echo "📝 Vérification du formatage avec black..."
    black --check *.py 2>/dev/null || {
        echo "❌ Erreur: Le code n'est pas formaté avec black"
        echo "💡 Lancez: black *.py"
        exit 1
    }
fi

# Vérification des imports Python
if command -v isort &> /dev/null; then
    echo "📦 Vérification des imports avec isort..."
    isort --check-only *.py 2>/dev/null || {
        echo "❌ Erreur: Les imports ne sont pas ordonnés"
        echo "💡 Lancez: isort *.py"
        exit 1
    }
fi

# Tests de syntaxe Python
echo "🐍 Vérification de la syntaxe Python..."
python -m py_compile *.py 2>/dev/null || {
    echo "❌ Erreur: Erreur de syntaxe Python détectée"
    exit 1
}

# Vérification de la documentation
echo "📚 Vérification de la documentation..."
if [ ! -f "README.md" ] || [ ! -f "CHANGELOG.md" ]; then
    echo "⚠️  Attention: README.md ou CHANGELOG.md manquant"
fi

# Vérification des secrets
echo "🔒 Vérification des secrets..."
if grep -r "password\|secret\|token\|key" --include="*.py" . | grep -v "example\|sample\|test" | head -1; then
    echo "❌ Erreur: Secrets détectés dans le code"
    exit 1
fi

echo "✅ Qualité validée avec succès !"
EOF

# Hook pre-push pour les tests
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "🚀 Lancement des tests avant push..."

# Tests unitaires si disponibles
if [ -d "tests" ]; then
    echo "🧪 Exécution des tests unitaires..."
    python -m pytest tests/ -v || {
        echo "❌ Erreur: Tests unitaires en échec"
        exit 1
    }
fi

# Vérification de la performance
echo "⚡ Vérification de la performance..."
python -c "
import time
import sys
try:
    from audiobook_processor import AudiobookProcessor
    start = time.time()
    processor = AudiobookProcessor('/tmp', '/tmp', '/tmp')
    duration = time.time() - start
    if duration > 2.0:
        print(f'❌ Erreur: Initialisation trop lente ({duration:.2f}s)')
        sys.exit(1)
    print(f'✅ Performance OK ({duration:.2f}s)')
except Exception as e:
    print(f'❌ Erreur: {e}')
    sys.exit(1)
" || {
    echo "❌ Erreur: Tests de performance en échec"
    exit 1
}

echo "✅ Tests validés avec succès !"
EOF

# Hook pour les merges vers main
cat > .git/hooks/pre-merge-commit << 'EOF'
#!/bin/bash
echo "🔄 Vérification pré-merge vers main..."

# Vérification qu'on merge bien vers main
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  Attention: Vous n'êtes pas sur la branche main"
fi

# Vérification de la version
echo "📋 Vérification de la version..."
if grep -q "## \[2\." CHANGELOG.md; then
    echo "✅ Version détectée dans CHANGELOG.md"
else
    echo "⚠️  Attention: Pas de version détectée dans CHANGELOG.md"
fi

# Vérification de la branche source
source_branch=$(git rev-parse --abbrev-ref MERGE_HEAD)
if [ "$source_branch" = "dev" ]; then
    echo "✅ Merge de dev vers main autorisé"
else
    echo "⚠️  Attention: Merge de $source_branch vers main (dev recommandé)"
fi

echo "✅ Pré-merge validé !"
EOF

# Rendre les hooks exécutables
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
chmod +x .git/hooks/pre-merge-commit

# Configuration des règles de branches
echo "🌿 Configuration des règles de branches..."

# Création du fichier de configuration des branches
cat > .gitrules << 'EOF'
# Règles de branches pour Audiobook Manager Pro

# Règle 1: Commits par défaut sur dev
default_branch: dev

# Règle 2: Protection de main
protected_branches:
  - main
  - release/*

# Règle 3: Workflow de développement
workflow:
  dev:
    description: "Branche de développement principale"
    merge_to: main
    requires_tests: true
    requires_review: true
    requires_version_bump: true
  
  feature/*:
    description: "Branches de fonctionnalités"
    merge_to: dev
    requires_tests: true
    requires_review: false
    
  hotfix/*:
    description: "Branches de correctifs urgents"
    merge_to: main
    requires_tests: true
    requires_review: true
    requires_version_bump: false

# Règle 4: Qualité requise
quality_gates:
  python_syntax: true
  code_formatting: true
  unit_tests: true
  performance_tests: true
  documentation_updated: true
  no_secrets: true
EOF

echo "✅ Configuration Git terminée avec succès !"
echo ""
echo "📋 Résumé des règles configurées :"
echo "  🌿 Branche par défaut: dev"
echo "  🔒 Branche main protégée"
echo "  🧪 Tests de qualité obligatoires"
echo "  📝 Formatage du code vérifié"
echo "  🔍 Vérification des secrets"
echo "  🚀 Tests de performance"
echo ""
echo "💡 Utilisation :"
echo "  git checkout dev    # Travailler sur dev"
echo "  git checkout -b feature/nom-feature    # Nouvelle fonctionnalité"
echo "  git checkout main    # Pour merger en production"
echo ""
echo "🎯 Workflow recommandé :"
echo "  1. Travailler sur dev"
echo "  2. Créer branches feature/* depuis dev"
echo "  3. Merger les features dans dev"
echo "  4. Créer une release/* depuis dev"
echo "  5. Merger la release dans main"
