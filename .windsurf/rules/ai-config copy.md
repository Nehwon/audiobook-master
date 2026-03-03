# Configuration IA pour Audiobook Manager Pro

## 🤖 Modèles et Prompts

### 📚 Génération Synopsis
```yaml
synopsis_generation:
  model: "llama2:7b"  # Modèle Ollama par défaut
  max_tokens: 300
  temperature: 0.7
  top_p: 0.9
  
  prompts:
    default: |
      Génère un synopsis de 150-300 mots pour "{title}" de "{author}".
      Style: Littéraire mais accessible.
      Pas de spoilers d'intrigue finale.
      Langue: {language}
      3 paragraphes maximum.
      
    french: |
      Génère un synopsis en français pour "{title}" de "{author}".
      Style littéraire accessible, 150-300 mots.
      Structure: Introduction, développement, conclusion.
      Éviter absolument les spoilers.
      
    english: |
      Generate a 150-300 word synopsis for "{title}" by "{author}".
      Literary but accessible style.
      3 paragraphs maximum.
      No spoilers included.
```

### 🏷️ Classification Genres
```yaml
genre_classification:
  model: "llama2:7b"
  max_tokens: 100
  temperature: 0.3  # Plus bas pour cohérence
  
  genres_mapping:
    fiction: ["Roman", "Science-fiction", "Fantasy", "Policier", "Thriller"]
    non_fiction: ["Biographie", "Histoire", "Essai", "Documentaire", "Science"]
    young_adult: ["Jeunesse", "Adolescent", "Fantasy YA"]
    children: ["Enfants", "Contes", "Éducatif"]
    
  prompt: |
    Analyse "{title}" de "{author}" et classifie dans les catégories suivantes:
    {genres_list}
    
    Retourne format JSON:
    {{
      "primary_genre": "genre_principal",
      "secondary_genres": ["genre_secondaire1", "genre_secondaire2"],
      "confidence": 0.85,
      "reasoning": "explication brève"
    }}
```

### 📝 Métadonnées Enrichies
```yaml
metadata_enrichment:
  model: "llama2:7b"
  max_tokens: 200
  temperature: 0.5
  
  prompt: |
    Enrichis les métadonnées pour "{title}" de "{author}".
    
    Informations disponibles:
    - Titre: {title}
    - Auteur: {author}
    - Série: {series}
    - Description existante: {existing_description}
    
    Génère:
    1. Description optimisée (500 caractères max)
    2. Tags pertinents (max 10)
    3. Classification d'âge
    4. Thèmes principaux
    
    Format JSON:
    {{
      "description": "description_optimisée",
      "tags": ["tag1", "tag2", ...],
      "age_rating": "tout_public | adolescent | adulte",
      "themes": ["theme1", "theme2", ...]
    }}
```

## 🔍 Validation et Qualité

### ✅ Checks Automatiques
```yaml
validation_rules:
  synopsis:
    min_length: 50
    max_length: 300
    forbidden_words: ["spoiler", "meurt", "fin", "révélation"]
    required_elements: ["introduction", "développement"]
    
  metadata:
    max_genres: 3
    max_tags: 10
    max_description_length: 500
    required_fields: ["title", "author", "description"]
    
  covers:
    min_resolution: "600x600"
    max_file_size: 2097152  # 2MB
    allowed_formats: ["jpg", "jpeg", "png"]
```

### 📊 Scoring Qualité
```python
def calculate_quality_score(metadata, synopsis, cover):
    """Calcule score de qualité 0-100"""
    score = 0
    
    # Métadonnées complètes (40 points)
    if all([metadata.title, metadata.author, metadata.description]):
        score += 20
    if len(metadata.genres) >= 1 and len(metadata.genres) <= 3:
        score += 10
    if len(metadata.tags) >= 3:
        score += 10
    
    # Synopsis qualité (30 points)
    synopsis_words = len(synopsis.split())
    if 50 <= synopsis_words <= 300:
        score += 15
    if not any(word in synopsis.lower() for word in ["spoiler", "fin"]):
        score += 15
    
    # Pochette (30 points)
    if cover and cover_resolution >= (600, 600):
        score += 20
    if cover_size <= 2 * 1024 * 1024:  # 2MB
        score += 10
    
    return min(score, 100)
```

## 🌐 Multi-sources Configuration

### 📚 Sources Scraping
```yaml
scraping_sources:
  priority_order:
    - google_books
    - babelio  # Si français
    - open_library
    - audible
    
  google_books:
    enabled: true
    api_key_env: "GOOGLE_BOOKS_API_KEY"
    rate_limit: 100  # requêtes/heure
    timeout: 10
    
  babelio:
    enabled: true
    base_url: "https://www.babelio.com"
    rate_limit: 60
    timeout: 15
    languages: ["fr"]
    
  open_library:
    enabled: true
    base_url: "https://openlibrary.org"
    rate_limit: 100
    timeout: 10
    
  audible:
    enabled: false  # Nécessite authentification
    rate_limit: 30
    timeout: 20
```

### 🔄 Cross-validation
```python
def cross_validate_metadata(sources_data):
    """Valide métadonnées depuis multiples sources"""
    validated = {}
    
    # Titre (doit être identique)
    titles = [data.get('title') for data in sources_data if data.get('title')]
    if len(set(titles)) == 1:
        validated['title'] = titles[0]
    else:
        validated['title'] = most_common(titles)
        validated['title_conflict'] = True
    
    # Auteur (doit être identique)
    authors = [data.get('author') for data in sources_data if data.get('author')]
    if len(set(authors)) == 1:
        validated['author'] = authors[0]
    else:
        validated['author'] = most_common(authors)
        validated['author_conflict'] = True
    
    # Description (choisir la plus complète)
    descriptions = [data.get('description') for data in sources_data if data.get('description')]
    if descriptions:
        validated['description'] = max(descriptions, key=len)
        validated['description_sources'] = len(descriptions)
    
    return validated
```

## 🎯 Optimisation Performance

### ⚡ Caching Strategy
```yaml
caching:
  metadata_cache:
    ttl: 86400  # 24 heures
    max_size: 1000  # entrées
    storage: "redis"  # ou "file"
    
  synopsis_cache:
    ttl: 604800  # 7 jours
    max_size: 500
    storage: "file"
    
  cover_cache:
    ttl: 2592000  # 30 jours
    max_size: 200
    storage: "file"
```

### 🚀 Batch Processing
```python
async def batch_process_metadata(items):
    """Traite métadonnées en parallèle"""
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent
    
    async def process_single(item):
        async with semaphore:
            return await enrich_metadata(item)
    
    tasks = [process_single(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

## 🔒 Configuration Sécurité

### 🛡️ Validation Entrées
```python
def validate_ai_input(text):
    """Valide et nettoie entrée pour IA"""
    # Longueur maximale
    if len(text) > 1000:
        raise ValueError("Texte trop long")
    
    # Caractères dangereux
    dangerous_chars = ['<', '>', '&', '"', "'", '`']
    if any(char in text for char in dangerous_chars):
        text = escape_html(text)
    
    # Injection prompts
    injection_patterns = ["ignore previous", "system:", "assistant:"]
    if any(pattern.lower() in text.lower() for pattern in injection_patterns):
        raise ValueError("Pattern d'injection détecté")
    
    return text.strip()
```

### 🔐 API Keys Management
```yaml
api_keys:
  google_books:
    env_var: "GOOGLE_BOOKS_API_KEY"
    required: false
    description: "Clé API Google Books pour métadonnées"
    
  ollama:
    env_var: "OLLAMA_BASE_URL"
    default: "http://localhost:11434"
    required: true
    description: "URL du serveur Ollama"
```

## 📊 Monitoring et Analytics

### 📈 Métriques IA
```python
class AIMetrics:
    def __init__(self):
        self.requests_count = 0
        self.success_count = 0
        self.error_count = 0
        self.avg_response_time = 0
        self.cache_hit_rate = 0
    
    def record_request(self, success, response_time, cache_hit=False):
        self.requests_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        # Moyenne mobile temps réponse
        self.avg_response_time = (
            (self.avg_response_time * (self.requests_count - 1) + response_time) 
            / self.requests_count
        )
        
        if cache_hit:
            self.cache_hit_rate = (
                (self.cache_hit_rate * (self.requests_count - 1) + 1) 
                / self.requests_count
            )
```

### 🚨 Alertes Qualité
```yaml
alerts:
  low_quality_threshold: 70  # Score qualité < 70%
  high_error_rate: 0.1  # >10% erreurs
  slow_response_time: 30  # >30 secondes
  cache_miss_rate: 0.8  # >80% cache miss
  
  notifications:
    webhook_url: "${DISCORD_WEBHOOK_URL}"
    email_recipients: ["admin@example.com"]
```

---
*Configuration IA maintenue activement*  
*Version: 2.0.0*  
*Dernière mise à jour: 2026-03-01*
