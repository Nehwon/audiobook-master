# 📌 Stratégie de Reprise Automatique

## 📡 Objectifs

1. **Automatiser la reprise des traitements interrompus** : Sécuriser l'exécution et éviter les pertes de données.
2. **Détecter les jobs `running` orphelins** : Vérifier les jobs en cours sans heartbeat.
3. **Politique de retry configurable** : Max tentatives, backoff.
4. **Verrous/logique d'idempotence** : Éviter les doubles traitements.
5. **Journal d'audit des reprises automatiques** : Historique des actions de reprise.

## 📡 Mécanisme de Recovery au Démarrage

1. **Détection des jobs `running` orphelins** :
   - Vérification des jobs en cours sans heartbeat.
   - Passage en `retry_pending` ou reprise directe selon politique.

2. **Politique de Retry Configurable** :
   - Max tentatives.
   - Backoff.

3. **Verrous/Logique d'Idempotence** :
   - Éviter les doubles traitements.

4. **Journal d'Audit des Reprises Automatiques** :
   - Historique des actions de reprise.

## 📡 Stratégie de Reprise Initiale

- **Safe Retry** : Reprise automatique pour les cas nominalement retryables.
- **Manual Intervention** : Intervention manuelle pour les cas critiques.

## 📡 Endpoint Admin

- `GET /api/recovery/status` : État de la reprise automatique.

## 📡 Tests d'Intégration

- **Crash/Restart** : Tests d'intégration pour simuler des crashes et des relances.
- **Idempotence** : Vérifier qu'il n'y a pas de duplication de sorties pour un même job.

## 📝 Conclusion

La stratégie de reprise automatique permet de sécuriser l'exécution et de garantir la continuité des traitements. Les prochaines étapes consistent à valider cette stratégie et à commencer l'implémentation des nouvelles fonctionnalités.
