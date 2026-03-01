# Règles de Push et Merge - Audiobook Manager Pro

## 🔒 Règles de Push GitHub

### 🚫 **Restriction Push GitHub**
- **Jamais de push direct** vers GitHub sans demande explicite
- **Confirmation obligatoire** de l'auteur (Fabrice) avant tout push GitHub
- **Exception** : Uniquement pour releases majeures validées
- **Workflow** : Toujours push vers Gitea en premier

### 📋 **Processus de Push**

#### 1. Développement Normal
```bash
# ✅ Push vers Gitea (dépôt principal)
git push origin dev
git push origin feature/nom-feature

# ❌ Push GitHub interdit sans confirmation
git push github  # BESOIN CONFIRMATION
```

#### 2. Demande de Push GitHub
```bash
# Étape 1: Préparer le push
git status
git log --oneline -5

# Étape 2: Demander confirmation
# Message à l'auteur:
# "Demande de push GitHub pour la branche [nom-branche]
# Contenu: [description des changements]
# Validation: [tests passés, documentation mise à jour]"

# Étape 3: Attendre confirmation explicite
# Réponse attendue: "OK pour push GitHub [branche]"

# Étape 4: Push autorisé
git push github [branche]
```

#### 3. Release Majeure
```bash
# Cas exceptionnel: Release majeure
git checkout main
git tag v2.1.0
git push github main --tags
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
git push github main --tags  # Avec confirmation
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
git push github main  # Avec confirmation
```

## 🔐 Validation Automatique

### ✅ **Checklist Pre-Push GitHub**
```bash
# Script de validation (à implémenter)
#!/bin/bash

# Vérifier branche actuelle
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ] && [ "$current_branch" != "dev" ]; then
    echo "❌ Push GitHub uniquement depuis main ou dev"
    exit 1
fi

# Vérifier si demande confirmée
if [ ! -f ".github_push_confirmed" ]; then
    echo "❌ Demander confirmation avant push GitHub"
    exit 1
fi

# Vérifier tests
if ! pytest tests/ --quiet; then
    echo "❌ Tests en échec - Push GitHub interdit"
    exit 1
fi

echo "✅ Push GitHub autorisé"
rm .github_push_confirmed
```

### 📝 **Template Demande Confirmation**
```markdown
## Demande de Push GitHub

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
**Demande de confirmation**: [ ] OK pour push GitHub
**Validé par**: ________________________
**Date**: ________________________
```

## 🔄 Workflow Complet

### 📅 **Développement Quotidien**
1. **Travailler** sur branches feature depuis dev
2. **Push** vers origin (Gitea) régulièrement
3. **Merge** dans dev après review
4. **Jamais de push GitHub** sans demande

### 🚀 **Release Process**
1. **Finaliser** features dans dev
2. **Tester** complètement sur dev
3. **Demander** merge vers main
4. **Attendre** validation utilisateur
5. **Merger** dans main
6. **Demander** push GitHub
7. **Push** vers GitHub après confirmation

### 📊 **Monitoring**
- **Log des demandes** : Fichier `.github_push_requests.log`
- **Historique des merges** : Fichier `.merge_history.log`
- **Validation automatique** : Hook pre-push GitHub

## 🚨 Sanctions

### ⚠️ **Push GitHub non autorisé**
- **Warning** : Message d'erreur explicite
- **Blocage** : Hook Git bloque le push
- **Notification** : Email/message à l'équipe

### 🔄 **Processus de régularisation**
1. **Analyser** le push non autorisé
2. **Créer** demande de confirmation rétroactive
3. **Valider** les changements
4. **Autoriser** le push après validation

---
*Règles strictes pour qualité et sécurité*  
*Version: 1.0*  
*Date: 2026-03-01*
