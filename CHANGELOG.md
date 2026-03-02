# 📝 Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [2.0.1] - 2026-03-02

### 🧪 AJOUTÉ
- **Tests Unitaires** : Suite complète de tests unitaires avec pytest
- **Coverage Reporting** : Configuration pytest-cov pour métriques de couverture
- **Tests Configuration** : 100% coverage pour core/config.py ✅
- **Tests Processor** : Tests conversion, parsing, GPU detection (30% coverage)
- **Tests Metadata** : Tests validation et formatage métadonnées
- **Tests Main CLI** : Tests arguments et ligne de commande
- **Virtual Environment** : Configuration venv standard avec requirements_test.txt
- **Documentation Tests** : README.md mis à jour avec commandes de test

### 🔧 AMÉLIORÉ
- **Structure Python** : Imports relatifs corrigés dans tous les modules
- **Module Organization** : __init__.py ajoutés pour structure Python propre
- **Error Handling** : Corrections bugs dans convert_to_m4b (total_input_size, GPU detection)
- **Code Quality** : Préparation pour coverage 90% avec tests étendus

### 📊 MÉTRIQUES
- **Coverage Global** : 16% (objectif 90%)
- **Tests Fonctionnels** : 13/15 tests passent (87%)
- **Modules Testés** : core/config.py (100%), core/processor.py (30%)

---

## [2.0.0] - 2026-03-01

### 🎉 AJOUTÉ
- **Interface Web Moderne** : Dashboard complet avec Flask + SocketIO
- **Monitoring Temps Réel** : Barre de progression avec indicateurs CPU/GPU
- **API REST Complète** : 8 endpoints pour gestion des conversions
- **WebSocket Intégré** : Communication temps réel avec le frontend
- **Options de Conversion Web** : Bitrate, échantillonnage, GPU, normalisation
- **Téléchargement Direct** : Download des fichiers M4B depuis l'interface
- **Notifications** : Alertes en temps réel des conversions
- **Design Responsive** : Interface mobile-friendly avec Tailwind CSS
- **Performance Analytics** : Statistiques MB/min avec classification
- **Smart Progress** : Seuil d'arrêt intelligent (90% + 30s)

### 🚀 AMÉLIORÉ
- **Performance FFmpeg** : Optimisation des filtres et encodage FDK-AAC VBR4
- **Détection GPU** : Support RTX 4070/3050 amélioré avec monitoring
- **Barre de Progression** : Plus précise, fiable et non-bloquante
- **Parsing Métadonnées** : Format série "Auteur - Série - Tome X - Titre" amélioré
- **Gestion Erreurs** : Meilleure gestion des exceptions et recovery
- **Documentation** : README complet avec API documentation
- **Architecture** : Séparation CLI/Web pour meilleure maintenabilité

### � CORRIGÉ
- **Boucle Infinie** : Problème de progression résolu avec seuil d'arrêt
- **Syntaxe Python** : Erreurs de structure et brackets manquants corrigés
- **Memory Leaks** : Optimisation mémoire dans les threads de monitoring
- **GPU Detection** : Faux positifs éliminés, détection fiable
- **File Locking** : Problèmes d'accès concurrents résolus
- **Progress Bug** : Barre bloquée à 100% fixée

### 🔧 TECHNIQUE
- **Flask 2.3.3** : Framework web moderne et léger
- **SocketIO 5.3.6** : WebSocket temps réel bidirectionnel
- **Tailwind CSS** : Design system moderne utilitaire-first
- **Font Awesome 6** : Icônes professionnelles et cohérentes
- **Architecture Modulaire** : Séparation claire CLI/Web/API

---

## [1.5.0] - 2026-02-28

### 🎉 AJOUTÉ
- **Accélération GPU NVIDIA** : Support RTX 4070/3050 avec détection automatique
- **Monitoring CPU/GPU** : Indicateurs d'activité en temps réel (🔥 ACTIF/⚡ NORMAL/🐢 LENT/⏸️ PAUSE)
- **Performance Analytics** : Statistiques de conversion détaillées avec MB/min
- **Smart Progress** : Barre de progression basée sur la taille fichier et seuil intelligent

### 🚀 AMÉLIORÉ
- **FFmpeg Integration** : Utilisation FDK-AAC VBR4 par défaut pour qualité optimale
- **Compression Ratio** : Jusqu'à 80% de réduction avec bitrate flexible
- **Error Handling** : Gestion robuste des erreurs avec messages clairs
- **Logging** : Logs détaillés avec timestamps et progression

### � CORRIGÉ
- **Progress Bug** : Barre bloquée à 100% dès le début
- **GPU Utilization** : GPU non détecté correctement malgré disponibilité
- **Memory Usage** : Optimisation mémoire dans les longues conversions

---

## [1.0.0] - 2024-02-28

### Ajouté
- 🎵 Conversion M4B avec métadonnées FFmpeg
- 📚 Scraping Babelio pour métadonnées françaises
- 🤖 Génération de synopsis avec Ollama (IA locale)
- 🖼️ Téléchargement et traitement des pochettes
- ⬆️ Upload automatique vers Audiobookshelf
- 🔄 Renommage automatique des fichiers
- 📁 Support des archives ZIP/RAR

### Changé
- 🏗️ Architecture modulaire avec classes séparées
- ⚙️ Configuration centralisée dans `config.py`
- 📝 Amélioration des logs et messages utilisateur

---

## [0.9.0] - 2024-02-20

### Ajouté
- 🎵 Conversion audio de base vers M4B
- 📁 Support des formats MP3, M4A, WAV
- 🔄 Renommage simple des fichiers
- 📋 Logs de base

### Corrigé
- 🐛 Correction gestion des chemins Windows/Linux
- 🐛 Correction encodage des caractères spéciaux

---

## [0.5.0] - 2024-02-10

### Ajouté
- 🎵 Prototype de conversion audio
- 📁 Détection des fichiers audio
- 📋 Logs de base

---

## [1.5.0] - 2026-02-28
