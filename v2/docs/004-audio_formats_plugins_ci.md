# 🎚️ Matrice formats audio (état actuel)

## Entrées supportées

| Extension | Support |
|---|---|
| `.mp3` | ✅ |
| `.m4a` | ✅ |
| `.m4b` | ✅ |
| `.wav` | ✅ |
| `.flac` | ✅ |
| `.aac` | ✅ |
| `.ogg` | ✅ |

## Archives supportées (web)

| Extension | Support |
|---|---|
| `.zip` | ✅ |
| `.rar` | ✅ (via `rarfile`) |

## Sortie principale

| Format | Détails |
|---|---|
| `.m4b` | Format cible pipeline principal |

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

# 🔁 CI/CD (pragmatique)

## Objectif

Garantir un socle de qualité reproductible sur le dépôt actuel.

## Checks minimaux recommandés

```bash
pytest -q tests/test_smoke_suite.py
pytest -q tests/test_web_api.py tests/test_runtime_paths.py
```

## Pipeline cible

1. Installation dépendances
2. Lancement smoke suite
3. Lancement sous-ensemble API/config
4. (Optionnel) suite complète selon fenêtre de build

## Critères de merge

- ✅ Smoke suite verte
- ✅ Aucun changement non documenté sur API/CLI
- ✅ Documentation mise à jour si comportement modifié

## Notes

Le projet contient une suite large ; la stratégie pratique est de sécuriser d'abord un noyau stable, puis d'élargir progressivement les checks obligatoires.
