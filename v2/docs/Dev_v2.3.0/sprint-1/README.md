# 📌 Plan d'exécution Sprint 1 - Fondations PostgreSQL + Persistance d'États

## 🎯 Objectifs

1. **Mettre en place PostgreSQL** : Connexion PostgreSQL intégrée à l'application.
2. **Créer des migrations SQL versionnées** : Migrations SQL versionnées (ex: Alembic).
3. **Créer des tables initiales** : Tables initiales `processing_job`, `processing_step`, `folder_state`, `validation_result`, `processing_error`, `outbox_event`.
4. **Écrire des états clés pendant les traitements** : Écriture transactionnelle des états clés pendant les traitements.

## 📅 Planning estimé

- **Sprint 1**: Fondations PostgreSQL + persistance d'états (2 semaines).

## 📊 KPIs de succès

- En cas de redémarrage, les jobs en cours sont visibles en base avec état cohérent.
- Les erreurs sont historisées et requêtables par dossier/job.

## 📝 Livrables

- Connexion PostgreSQL intégrée à l'application.
- Migrations SQL versionnées (ex: Alembic).
- Tables initiales `processing_job`, `processing_step`, `folder_state`, `validation_result`, `processing_error`, `outbox_event`.
- Écriture transactionnelle des états clés pendant les traitements.

## 🚀 Prochaines étapes

1. **Ajouter couche repository/service** : Découpler la logique métier de la DB.
2. **Persister transitions d'état** : Persister les transitions d'état (queued, running, failed, done, cancelled).
3. **Persister erreurs techniques + fonctionnelles** : Persister les erreurs techniques + fonctionnelles avec contexte (stacktrace optionnelle + message utilisateur).
4. **Ajouter index sur colonnes de recherche** : Ajouter des index sur les colonnes de recherche (status, updated_at, folder_id).
5. **Préparer scripts de bootstrap et migration** : Préparer des scripts de bootstrap et de migration des environnements (docker-compose inclus).

## 📝 Conclusion

Le sprint 1 consiste à mettre en place PostgreSQL et à persister les états clés pendant les traitements. Les prochaines étapes consistent à valider cette mise en place et à commencer l'implémentation des nouvelles fonctionnalités.
