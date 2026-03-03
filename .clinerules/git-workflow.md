# Règles de Push et Merge - Audiobook Manager Pro

## 🔒 Règles de Push Gitea

### 📋 **Processus de Push**

#### 1. Développement Normal
```bash
# ✅ Push vers Gitea (dépôt principal)
git push origin dev
git push origin feature/nom-feature

# 🔄 Workflow standard
git add .
git commit -m "feat: description du changement"
git push origin dev
```

#### 2. Release Majeure
```bash
# Cas exceptionnel: Release majeure
git checkout main
git merge --no-ff dev
git tag v2.1.0
git push origin main --tags
```

## 🌿 Règles de Branches

### 📥 **Push vers dev**
- **Tous les commits** doivent passer par dev
- **Jamais de push direct** vers main depuis feature branches
- **Workflow obligatoire** : feature → dev → main

#### Processus Développement
```bash
# 1. Créer branche feature depuis dev
git checkout dev
git pull origin dev
git checkout -b feature/nouvelle-fonctionnalite

# 2. Développement et commits
git add .
git commit -m "feat: ajoute fonctionnalité X"

# 3. Push vers dev (après review)
git checkout dev
git merge --no-ff feature/nouvelle-fonctionnalite
git push origin dev
```

### 🎯 **Merge vers main**

#### 🚨 **Cas 1: Changement Majeur Validé**
- **Condition** : Release majeure (v2.1.0, v3.0.0, etc.)
- **Validation** : Confirmée par l'utilisateur (Fabrice)
- **Processus** : Merge automatique autorisé

```bash
# Release majeure validée
git checkout main
git merge --no-ff dev
git tag v2.1.0
git push origin main --tags
```

#### 📋 **Cas 2: Changement Standard**
- **Condition** : Features normales, corrections, améliorations
- **Processus** : Demande explicite obligatoire
- **Validation** : Confirmation utilisateur requise

```bash
# Demande de merge vers main
# Message à l'auteur:
# "Demande de merge dev → main"
# "Contenu: [liste des changements]"
# "Impact: [description de l'impact]"
# "Tests: [statut des tests]"

# Après confirmation:
git checkout main
git merge --no-ff dev
git push origin main
```

## 🔐 Validation Automatique

### ✅ **Checklist Pre-Merge**
```bash
# Script de validation (à implémenter)
#!/bin/bash

# Vérifier branche actuelle
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ] && [ "$current_branch" != "dev" ]; then
    echo "❌ Merge uniquement depuis main ou dev"
    exit 1
fi

# Vérifier si demande confirmée
if [ ! -f ".merge_confirmed" ]; then
    echo "❌ Demander confirmation avant merge"
    exit 1
fi

# Vérifier tests
if ! pytest tests/ --quiet; then
    echo "❌ Tests en échec - Merge interdit"
    exit 1
fi

echo "✅ Merge autorisé"
rm .merge_confirmed
```

### 📝 **Template Demande Confirmation**
```markdown
## Demande de Merge

**Branche**: [nom-branche]
**Auteur**: [développeur]
**Date**: [date]

### 📋 Changements
- [ ] Changement 1
- [ ] Changement 2
- [ ] Documentation mise à jour

### ✅ Validation
- [ ] Tests unitaires passés
- [ ] Tests d'intégration passés
- [ ] Performance vérifiée
- [ ] Sécurité validée

### 🎯 Impact
- **Utilisateurs**: [impact]
- **Performance**: [impact]
- **Sécurité**: [impact]

### 📊 Métriques
- **Coverage**: [x%]
- **Performance**: [MB/min]
- **Bugs résolus**: [x]

---
**Demande de confirmation**: [ ] OK pour merge
**Validé par**: ________________________
**Date**: ________________________
```

## 🔄 Workflow Complet

### 📅 **Développement Quotidien**
1. **Travailler** sur branches feature depuis dev
2. **Push** vers origin (Gitea) régulièrement
3. **Merge** dans dev après review
4. **Jamais de push direct** vers main sans validation

### 🚀 **Release Process**
1. **Finaliser** features dans dev
2. **Tester** complètement sur dev
3. **Demander** merge vers main
4. **Attendre** validation utilisateur
5. **Merger** dans main
6. **Taguer** la version
7. **Push** vers Gitea

### 📊 **Monitoring**
- **Log des demandes** : Fichier `.merge_requests.log`
- **Historique des merges** : Fichier `.merge_history.log`
- **Validation automatique** : Tests avant merges

---
*Règles adaptées pour dépôt Gitea unique*  
*Version: 2.0*  
*Date: 2026-03-02*
