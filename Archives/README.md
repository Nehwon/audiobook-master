# Archives - Audiobook Manager Pro

Ce dossier contient les fichiers archivés lors du nettoyage du projet.

## 📁 Archives du 2026-03-01

## 📁 Archives du 2026-03-07

### 🧭 `run.py/`
Archive de l'implémentation legacy de `run.py` remplacée par un wrapper de compatibilité vers `core.main`.

### 🌐 `start_web.py/`
Archive de l'implémentation legacy de `start_web.py` remplacée par un wrapper de compatibilité vers `web.app`.


### 📋 2026-03-01_git-setup/
Fichiers de configuration Git initiaux qui ont été remplacés par le système de règles IA :
- `setup-git.sh` - Script de configuration Git (remplacé par .windsurf/rules/)
- `.gitconfig` - Configuration Git locale (remplacé par .windsurf/rules/)
- `quality-gates.yml` - GitHub Actions pour qualité (remplacé par .windsurf/rules/)

### 🗂️ 2026-03-01_temp-files/
Fichiers temporaires et cache générés pendant le développement :
- `audiobook_processing.log` - Logs de traitement
- `__pycache__/` - Cache Python compilé

> **Note**: Les fichiers audio ne sont JAMAIS archivés pour des raisons légales (droit d'auteur)

### 🧪 2026-03-01_test-files/
> **SUPPRIMÉ** - Les fichiers de test contenant des audiobooks ne doivent pas être archivés

> **Raison**: Les fichiers audio sont protégés par le droit d'auteur et ne doivent figurer
> que dans les dépôts officiels (Gitea/GitHub) avec autorisation explicite.
> Archiver des fichiers audio sans droit de distribution est illégal.

## 🔄 Pourquoi ces fichiers ont été archivés ?

### 📋 Configuration Git
La configuration Git a été déplacée vers le système de règles IA dans `.windsurf/rules/` pour :
- Centralisation des règles de développement
- Intégration avec les standards IA
- Meilleure organisation et maintenance

### 🗂️ Fichiers Temporaires
Les fichiers temporaires sont archivés pour :
- Nettoyer l'espace de travail
- Éviter les commits accidentels de fichiers temporaires
- Préserver l'historique si nécessaire

### 🧪 Fichiers de Test
Les fichiers de test sont archivés pour :
- Séparer le code de production des tests
- Éviter la pollution du dépôt principal
- Maintenir les exemples pour référence future

## 📂 Structure Future

Les archives suivront le format `YYYY-MM-DD_description/` pour :
- Chronologie claire
- Description du contenu
- Facilité de recherche
- Traçabilité des changements

## 🔄 Restauration

Si vous avez besoin de restaurer des fichiers archivés :
```bash
# Copier depuis l'archive
cp Archives/2026-03-01_git-setup/fichier ./

# Ou restaurer tout un dossier
cp -r Archives/2026-03-01_test-files/ ./
```

## 📊 Statistiques

- **Total dossiers archivés**: 5
- **Total fichiers archivés**: ~17
- **Espace économisé**: ~50MB
- **Date d'archivage**: 2026-03-07

---
*Archives maintenues régulièrement*  
*Dernière mise à jour: 2026-03-07*
