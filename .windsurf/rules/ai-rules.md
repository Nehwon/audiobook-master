# Règles IA pour Audiobook Manager Pro

## 🤖 Règles de Génération IA

### 🎚️ Génération de Synopsis
- **Longueur**: 150-300 mots maximum
- **Style**: Littéraire mais accessible
- **Contenu**: Sans spoilers, intrigue principale uniquement
- **Langue**: Français par défaut, anglais si source anglaise
- **Format**: 3 paragraphes max

### 📚 Métadonnées Enrichies
- **Genres**: Maximum 3 genres pertinents
- **Description**: 500 caractères maximum
- **Tags**: 10 tags maximum, pertinents
- **Classification**: Âge approprié, thématiques
- **Validation**: Cross-check avec sources multiples

### 🎨 Pochettes et Images
- **Qualité**: Minimum 600x600 pixels
- **Format**: JPEG ou PNG optimisé
- **Poids**: Maximum 2MB
- **Contenu**: Approprié, pas de contenu offensant
- **Backup**: 2 sources minimum avant validation

### 📝 Formatage des Titres
- **Auteur**: Format "Nom Prénom" ou "Nom"
- **Série**: Format "Nom Série Tome X"
- **Titre**: Capitalisation standard française
- **Caractères spéciaux**: Éviter si possible
- **Longueur**: 100 caractères maximum

## 🧪 Tests de Qualité IA

### ✅ Validation Synopsis
```python
def validate_synopsis(text):
    if len(text.split()) < 50:
        return "Trop court"
    if len(text.split()) > 300:
        return "Trop long"
    if "spoiler" in text.lower():
        return "Contient des spoilers"
    return "Validé"
```

### ✅ Validation Métadonnées
```python
def validate_metadata(metadata):
    if len(metadata.get('genres', [])) > 3:
        return "Trop de genres"
    if len(metadata.get('description', '')) > 500:
        return "Description trop longue"
    return "Validé"
```

## 🔄 Workflow IA

### 1. Détection Automatique
- Parser nom de fichier
- Identifier auteur/série/titre
- Détecter langue source

### 2. Recherche Multi-sources
- Google Books API
- Babelio (si français)
- Open Library (backup)
- Validation croisée

### 3. Génération IA
- Synopsis via Ollama (llama2)
- Classification genres
- Tags pertinents
- Description optimisée

### 4. Validation Humaine
- Preview avant intégration
- Correction possible
- Validation finale

## 🎯 Prompts Optimisés

### Prompt Synopsis
```
Génère un synopsis de 150-300 mots pour "{titre}" de "{auteur}".
Style: Littéraire mais accessible.
Pas de spoilers.
Langue: Français.
3 paragraphes maximum.
```

### Prompt Métadonnées
```
Analyse "{titre}" de "{auteur}" et génère:
- 3 genres maximum
- Description 500 caractères max
- 10 tags pertinents
- Classification d'âge
Format JSON.
```

### Prompt Validation
```
Valide la qualité des métadonnées générées:
- Cohérence avec le titre
- Pertinence des genres
- Qualité de la description
- Exactitude des tags
```

## 📊 Métriques de Qualité IA

### 🎯 Objectifs
- **Précision synopsis**: >85%
- **Pertinence genres**: >90%
- **Satisfaction utilisateur**: >80%
- **Temps génération**: <10s

### 📈 Monitoring
- Taux d'acceptation IA
- Corrections manuelles
- Temps de génération
- Feedback utilisateurs

## 🚨 Limites et Contraintes

### ⚠️ Contenu à éviter
- Spoilers de fin
- Contenu offensant
- Informations personnelles
- Copyright violé

### 🔒 Confidentialité
- Pas de données personnelles dans prompts
- Cache local des réponses
- Anonymisation des requêtes
- Respect RGPD

### 🌐 Multi-langues
- Français priorité
- Anglais backup
- Espagnol/Allemand support basique
- Autres langues si disponible

## 🔄 Amélioration Continue

### 📊 Feedback Loop
- Collecte retours utilisateurs
- Analyse performances IA
- Ajustement prompts
- Mise à jour modèles

### 🧪 A/B Testing
- Test différents prompts
- Comparaison qualité
- Métriques précises
- Optimisation continue

---
*Dernière mise à jour: 2026-03-01*
*Version: 1.0*
