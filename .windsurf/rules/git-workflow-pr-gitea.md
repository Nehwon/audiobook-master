# 🔄 Git Workflow - Pull Request Process

## 📋 **Règle Importante : Pull Request via Gitea**

### ⚠️ **INTERDICTION : Merge Direct CLI**
- **❌ JAMAIS** de fusionner directement avec `git merge` depuis CLI
- **❌ JAMAIS** de forcer le merge avec `git push --force`
- **❌ JAMAIS** de bypass le processus de PR

### ✅ **PROCESSUS OBLIGATOIRE : Pull Request Gitea**

#### **Étape 1 : Préparation**
```bash
# S'assurer d'être sur la branche de développement
git checkout dev
git add .
git commit -m "feat: description détaillée des changements"
git push origin dev
```

#### **Étape 2 : Création PR via Gitea**
1. **Ouvrir le navigateur** : https://gitea.lamachere.fr/fabrice/audiobooks-master
2. **Cliquer sur "Pull Requests"**
3. **Cliquer sur "New Pull Request"**
4. **Sélectionner** :
   - **Source branch** : `dev`
   - **Target branch** : `main`
5. **Remplir** le formulaire PR :
   - **Titre** : Descriptif et clair
   - **Description** : Détail des changements
   - **Labels** : Type de modification (feat, fix, docs, etc.)
6. **Cliquer sur "Create Pull Request"**

#### **Étape 3 : Review et Validation**
1. **Attendre le review** automatique (CI/CD)
2. **Vérifier** que tous les tests passent
3. **Demander review** si nécessaire
4. **Approuver** la PR si tout est bon

#### **Étape 4 : Merge via Gitea**
1. **Cliquer sur "Merge"** dans l'interface Gitea
2. **Sélectionner** le type de merge :
   - **Merge Pull Request** (recommandé)
   - **Squash and Merge** (pour nettoyer l'historique)
   - **Rebase and Merge** (pour historique linéaire)
3. **Confirmer** le merge
4. **Supprimer** la branche `dev` si demandé

---

## 🎯 **Pourquoi cette Règle ?**

### 🔒 **Sécurité et Traçabilité**
- **Historique clair** : Tous les merges sont tracés
- **Review obligatoire** : Pas de merge non contrôlé
- **Backup automatique** : Gitea gère les conflits
- **Rollback facile** : Possibilité de revenir en arrière

### 👥 **Collaboration**
- **Visibilité** : Tout le monde voit les changements
- **Discussion** : Possibilité de commenter les modifications
- **Validation** : Review par pairs avant intégration
- **Documentation** : PR sert de documentation

### 🤖 **Automatisation**
- **CI/CD** : Tests automatiques sur chaque PR
- **Qualité** : Vérification automatique du code
- **Intégration** : Processus standardisé
- **Monitoring** : Suivi des modifications

---

## 🚨 **Cas d'Exception**

### **Urgence Critique**
En cas d'urgence absolue (production down, sécurité critique) :

1. **Documenter** l'urgence dans un ticket
2. **Avertir** l'équipe immédiatement
3. **Justifier** pourquoi le processus PR ne peut pas être suivi
4. **Créer une PR rétroactive** après l'intervention

### **Correction Rapide**
Pour les petites corrections de documentation :

1. **Privilégier** toujours la PR
2. **Si vraiment nécessaire** : merge direct avec `--no-ff`
3. **Documenter** dans le commit message
4. **Créer PR** pour la suite des modifications

---

## 📋 **Checklist PR**

### **Avant de créer la PR**
- [ ] Code propre et testé
- [ ] Documentation mise à jour
- [ ] Tests unitaires passent
- [ ] Commit messages clairs
- [ ] Branche `dev` à jour

### **Pendant la PR**
- [ ] Titre descriptif
- [ ] Description détaillée
- [ ] Labels appropriés
- [ ] Reviewers assignés
- [ ] CI/CD vert

### **Après le merge**
- [ ] Supprimer branche `dev` si nécessaire
- [ ] Mettre à jour la documentation
- [ ] Annoncer les changements
- [ ] Archiver la PR

---

## 🔧 **Commandes Utiles**

### **Vérifier l'état avant PR**
```bash
# Vérifier que la branche est propre
git status

# Vérifier les différences avec main
git diff main...dev

# Vérifier les commits
git log main..dev --oneline
```

### **Préparation rapide**
```bash
# Mettre à jour main
git checkout main
git pull origin main

# Replier dev sur main
git checkout dev
git rebase main

# Pousser les changements
git push origin dev --force-with-lease
```

---

## 🎯 **Conclusion**

**Le processus de Pull Request via Gitea est OBLIGATOIRE** pour garantir :

- ✅ **Qualité** du code
- ✅ **Sécurité** des modifications
- ✅ **Traçabilité** de l'historique
- ✅ **Collaboration** efficace
- ✅ **Automatisation** du processus

**Toute violation de cette règle doit être justifiée et documentée.**

---

*Document maintenu activement • Dernière mise à jour : Mars 2026* 🔄