# Stratégie de migration UI (v1 -> v2) avec rollback immédiat

Cette stratégie permet d'activer progressivement la nouvelle interface sans perdre l'ancienne.

## Mécanisme implémenté
- `v1` (legacy) : `templates/index_v1.html`
- `v2` (preview) : `templates/index_v2.html`
- Sélecteur via query string : `/?ui=v1` ou `/?ui=v2`
- Persistance du choix utilisateur via cookie `audiobook_ui_version`
- Valeur par défaut configurable avec `AUDIOBOOK_UI_DEFAULT` (`v1` recommandé au début)
- Endpoint de diagnostic : `GET /api/ui/version`

## Plan de déploiement recommandé
1. **Semaine 1 (safe mode)**
   - Déployer avec `AUDIOBOOK_UI_DEFAULT=v1`.
   - Donner l'URL preview à un groupe pilote : `/?ui=v2`.
2. **Semaine 2 (canary)**
   - Monitorer erreurs backend + retours UX.
   - Corriger la v2 sans impacter la prod (v1 reste intacte).
3. **Go-live progressif**
   - Passer `AUDIOBOOK_UI_DEFAULT=v2`.
   - Conserver `/?ui=v1` comme rollback rapide.
4. **Retrait legacy**
   - Supprimer `index_v1.html` uniquement après stabilisation confirmée.

## Rollback instantané
- Global : remettre `AUDIOBOOK_UI_DEFAULT=v1`.
- Utilisateur : forcer `/?ui=v1`.

