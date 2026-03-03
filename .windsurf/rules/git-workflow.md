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

### 🎯 **Merge vers main - OBLIGATOIRE via Gitea PR**

#### ⚠️ **RÈGLE FONDAMENTALE**
- **🚨 INTERDICTION ABSOLUE** de merge direct depuis CLI
- **🚨 INTERDICTION ABSOLUE** de `git merge` sans PR
- **🚨 INTERDICTION ABSOLUE** de bypass du processus Gitea

#### ✅ **PROCESSUS OBLIGATOIRE : Pull Request Gitea**

##### **Étape 1 : Préparation**
```bash
# S'assurer d'être sur dev et pousser les changements
git checkout dev
git add .
git commit -m "feat: description détaillée des changements"
git push origin dev
```

##### **Étape 2 : Création PR via Gitea**
1. **Ouvrir** : https://gitea.lamachere.fr/fabrice/audiobooks-master
2. **Cliquer** sur "Pull Requests" → "New Pull Request"
3. **Sélectionner** :
   - **Source branch** : `dev`
   - **Target branch** : `main`
4. **Remplir** le formulaire :
   - **Titre** : Descriptif et clair
   - **Description** : Détail des changements
   - **Labels** : Type de modification
5. **Créer** la Pull Request

##### **Étape 3 : Review et Merge**
1. **Attendre** le review automatique (CI/CD)
2. **Vérifier** que tous les tests passent
3. **Approuver** la PR si tout est bon
4. **Cliquer sur "Merge" dans l'interface Gitea
5. **Sélectionner** le type de merge souhaité

#### 🚨 **Cas d'Exception Critique**
Uniquement en cas d'urgence absolue (production down, sécurité critique) :

1. **Documenter** l'urgence immédiatement
2. **Avertir** l'équipe
3. **Justifier** pourquoi la PR n'est pas possible
4. **Créer une PR rétroactive** après l'intervention

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
3. **Créer PR** vers main via Gitea
4. **Attendre** validation utilisateur
5. **Merger** via interface Gitea
6. **Taguer** la version
7. **Push** vers Gitea

### 📊 **Monitoring**
- **Log des demandes** : Fichier `.merge_requests.log`
- **Historique des merges** : Fichier `.merge_history.log`
- **Validation automatique** : Tests avant merges

---

## 📋 **Références**
- **Documentation complète** : `.windsurf/rules/git-workflow-pr-gitea.md`
- **Processus détaillé** : Étapes complètes PR Gitea
- **Checklist PR** : Validation avant merge

---
*Règles adaptées pour dépôt Gitea unique*  
*Version: 2.1*  
*Date: 2026-03-03*  
*Règle PR obligatoire ajoutée*