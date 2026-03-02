# 📝 Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [2.0.8] - 2026-03-02

### 🧪 AJOUTÉ
- **Tests Main Final** : 17 tests pour CLI, arguments, exceptions, dry-run, upload
- **Tests CLI Complète** : Traitement fichier unique et par lots
- **Tests Exceptions** : Gestion erreurs critiques et fichiers manquants
- **Tests Configuration** : Options avancées et validation
- **Tests Upload** : Configuration et gestion erreurs
- **Total** : 152 tests unitaires 100% fonctionnels

### 🔧 AMÉLIORÉ
- **Coverage Global** : 58% (record historique !) ⬆️ maintenu
- **Coverage Main.py** : 73% (presque 80% objectif)
- **Tests Robustesse** : Gestion complète des cas d'erreur
- **Tests CLI** : Couverture complète des options et arguments
- **Structure Tests** : Organisation modulaire et maintenable

### 📊 MÉTRIQUES
- **Coverage Global** : 58% (record historique !)
- **Tests Fonctionnels** : 152/152 tests passants (100%)
- **Modules Testés** : core/config.py (100%), core/metadata.py (43%), core/processor.py (67%), core/main.py (73%)

---

## [2.0.7] - 2026-03-02

### 🧪 AJOUTÉ
- **Tests Processor Final** : 22 tests pour conversion avancée et scraping
- **Tests Conversion** : GPU, FDK-AAC, chapitres, loudnorm, compression
- **Tests Synopsis** : Génération et désactivation
- **Tests Scraping** : Audible/Babelio avec fallback
- **Tests Téléchargement** : Pochettes et gestion erreurs
- **Total** : 152 tests unitaires 100% fonctionnels

### 🔧 AMÉLIORÉ
- **Coverage Global** : 58% (record historique !) ⬆️ maintenu
- **Coverage Processor** : 67% (presque 70% objectif)
- **Tests Robustesse** : Gestion erreurs subprocess et timeout
- **Tests Configuration** : Options avancées de conversion
- **Structure Tests** : Organisation modulaire et maintenable

### 📊 MÉTRIQUES
- **Coverage Global** : 58% (record historique !)
- **Tests Fonctionnels** : 152/152 tests passants (100%)
- **Modules Testés** : core/config.py (100%), core/metadata.py (43%), core/processor.py (67%), core/main.py (73%)

---

## [2.0.6] - 2026-03-02

### 🧪 AJOUTÉ
- **Tests Metadata Extended** : 21 tests étendus pour metadata.py
- **Tests Scraping** : Recherche et parsing Audible/Babelio
- **Tests BookInfo** : Création, validation et représentation
- **Tests Similarité** : Calcul de similarité et validation de correspondance
- **Tests Téléchargement** : Download et gestion des pochettes
- **Total** : 152 tests unitaires 100% fonctionnels

### 🔧 AMÉLIORÉ
- **Coverage Global** : 58% (objectif 90%) ⬆️ de 57% à 58%
- **Coverage Metadata** : 43% ⬆️ de 41% à 43%
- **Tests Complets** : scraping, parsing, validation, BookInfo
- **Tests Robustesse** : Gestion des erreurs HTTP et parsing
- **Structure Tests** : Organisation modulaire et maintenable

### 📊 MÉTRIQUES
- **Coverage Global** : 58% (objectif 90%)
- **Tests Fonctionnels** : 152/152 tests passants (100%)
- **Modules Testés** : core/config.py (100%), core/metadata.py (43%), core/processor.py (67%), core/main.py (73%)

---

## [2.0.5] - 2026-03-02

### 🧪 AJOUTÉ
- **Tests Main Extended** : 11 tests étendus pour main.py
- **Tests Upload** : Configuration et gestion upload Audiobookshelf
- **Tests Dry-Run** : Mode simulation pour fichiers et lots
- **Tests Exception Handling** : Gestion robuste des erreurs critiques
- **Tests Logging** : Configuration et vérification logging
- **Total** : 131 tests unitaires 100% fonctionnels

### 🔧 AMÉLIORÉ
- **Coverage Global** : 57% (objectif 90%) ⬆️ de 52% à 57%
- **Coverage Main.py** : 73% ⬆️ de 21% à 73% (objectif 50% dépassé !)
- **Tests Complets** : upload, dry-run, exceptions, logging, arguments
- **Tests Robustesse** : Gestion des cas limites et erreurs critiques
- **Structure Tests** : Organisation modulaire et maintenable

### 📊 MÉTRIQUES
- **Coverage Global** : 57% (objectif 90%)
- **Tests Fonctionnels** : 131/131 tests passants (100%)
- **Modules Testés** : core/config.py (100%), core/metadata.py (41%), core/processor.py (67%), core/main.py (73%)

---

## [2.0.4] - 2026-03-02

### 🧪 AJOUTÉ
- **Tests Processor Extended** : 10 tests étendus pour process_audiobook et process_all
- **Tests Configuration** : Tests avec configuration personnalisée
- **Tests Exception Handling** : Gestion des erreurs et exceptions
- **Total** : 120 tests unitaires 100% fonctionnels

### 🔧 AMÉLIORÉ
- **Coverage Global** : 52% (objectif 90%) ⬆️ de 43% à 52%
- **Coverage Processor** : 67% ⬆️ de 46% à 67% (presque 70% !)
- **Tests Complets** : process_audiobook, process_all, configuration, exceptions
- **Tests Robustesse** : Gestion des cas limites et erreurs
- **Structure Tests** : Organisation modulaire et maintenable

### 📊 MÉTRIQUES
- **Coverage Global** : 52% (objectif 90%)
- **Tests Fonctionnels** : 120/120 tests passants (100%)
- **Modules Testés** : core/config.py (100%), core/metadata.py (41%), core/processor.py (67%), core/main.py (21%)

---

## [2.0.3] - 2026-03-02

### 🧪 AJOUTÉ
- **Tests Processor Coverage** : 23 tests étendus pour processor.py
- **Tests Metadata Coverage** : 33 tests étendus pour metadata.py
- **Tests Main Coverage** : 12 tests étendus pour main.py
- **Total** : 110 tests unitaires 100% fonctionnels

### 🔧 AMÉLIORÉ
- **Coverage Global** : 43% (objectif 90%) ⬆️ de 34% à 43%
- **Coverage Processor** : 46% ⬆️ de 30% à 46%
- **Coverage Metadata** : 41% ⬆️ de 35% à 41%
- **Tests Complets** : parsing, extraction, GPU, pochette, synopsis, CLI
- **Structure Tests** : Organisation modulaire et maintenable

### 📊 MÉTRIQUES
- **Coverage Global** : 43% (objectif 90%)
- **Tests Fonctionnels** : 110/110 tests passants (100%)
- **Modules Testés** : core/config.py (100%), core/metadata.py (41%), core/processor.py (46%), core/main.py (21%)

---

## [2.0.2] - 2026-03-02

### 🧪 AJOUTÉ
- **54 Tests Unitaires** : Suite complète de tests 100% fonctionnels
- **Tests Metadata Scraper** : 31 tests pour Audible et Babelio scrapers
- **Tests Main Simplifiés** : 8 tests pour arguments CLI et parsing
- **Coverage Reporting** : Configuration complète avec pytest-cov

### 🔧 AMÉLIORÉ
- **Coverage Global** : 34% (objectif 90%) ⬆️ de 16% à 34%
- **Tests Processor** : 100% fonctionnels (3/3 tests)
- **Tests Metadata** : 100% fonctionnels (31/31 tests)
- **Tests Config** : 100% fonctionnels (5/5 tests)
- **Tests Main** : 100% fonctionnels (8/8 tests)
- **Structure Tests** : Organisation modulaire et maintenable

### 📊 MÉTRIQUES
- **Coverage Global** : 34% (objectif 90%)
- **Tests Fonctionnels** : 54/54 tests passants (100%)
- **Modules Testés** : core/config.py (100%), core/metadata.py (35%), core/processor.py (30%), core/main.py (21%)

---

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
