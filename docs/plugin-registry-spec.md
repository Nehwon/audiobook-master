# Sprint 4 — Spécification du registre plugins

Ce document lance les livrables Sprint 4 autour de l'écosystème plugins.

## Objectifs

- Prioriser le plugin d'export Audiobookshelf comme plugin officiel (`plugins.exports.AudiobookshelfExportPlugin`).
- Définir un registre JSON de découverte des plugins.
- Fournir un prototype d'installation de plugin depuis une source distante (archive `.zip`).

## Contrat de registre (v1)

Un registre est un JSON servi via HTTP(s) avec ce schéma logique:

```json
{
  "schema_version": "1.0",
  "plugins": [
    {
      "id": "example.plugin",
      "display_name": "Example Plugin",
      "description": "Description courte",
      "releases": [
        {
          "version": "1.2.0",
          "min_app_version": "0.9.0",
          "max_app_version": "2.0.0",
          "package_url": "https://example.com/example.plugin-1.2.0.zip",
          "sha256": "<checksum optionnel>"
        }
      ]
    }
  ]
}
```

## Compatibilité versions

Règles appliquées par le prototype:

- `min_app_version` (inclusive): la version de l'application doit être `>=`.
- `max_app_version` (exclusive): la version de l'application doit être `<`.
- Si une borne est absente, elle n'est pas vérifiée.

## Prototype d'installation distante

Implémentation: `plugins/marketplace.py`.

Capacités MVP:

1. Télécharge le registre (`PluginRegistryClient`).
2. Liste les plugins et leurs releases.
3. Vérifie la compatibilité app/release.
4. Télécharge une archive `.zip` de release.
5. Vérifie optionnellement le `sha256`.
6. Installe le plugin dans un répertoire cible local.

## Limites connues (MVP)

- Pas de signature cryptographique (hors checksum SHA256).
- Pas de sandbox d'exécution plugin.
- Pas de dépendances Python isolées par plugin.
- Pas de rollback atomique multi-version.
