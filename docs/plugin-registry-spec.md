# 🔌 Plugin registry spec (état v1)

## Types de plugins existants

- `metadata` : enrichissement métadonnées (Google Books, Audible, Babelio)
- `covers` : acquisition de couverture (fichier local, URL)
- `exports` : publication (Audiobookshelf)

## Contrat minimal attendu

- identifiant stable du plugin,
- interface base par famille (`base_scraper.py`, `base_cover.py`, `base_export.py`),
- gestion d'échec non bloquante (fallback plugin suivant),
- configuration sérialisable dans config web/CLI.

## Priorités pour registre/marketplace

1. Discovery (liste plugins + compatibilité version)
2. Installation contrôlée (source vérifiée)
3. Activation/désactivation par config
4. Audit trail (qui a installé quoi, quand)
