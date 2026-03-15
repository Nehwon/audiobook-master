# 📄 ADR 001 - Architecture React + PostgreSQL

## 🎯 Objectifs

1. **Passer l'UI en React** pour obtenir une interface réactive (mise à jour instantanée des traitements backend, états de dossiers, logs, erreurs).
2. **Passer sur PostgreSQL** pour persister les états d'exécution et de validation, reprendre automatiquement après incident/redémarrage, et afficher les erreurs de manière claire dans la zone **Dossiers**.

## 📅 Planning estimé

- **Sprint 0**: Cadrage technique et architecture (1 semaine).
- **Sprint 1**: Fondations PostgreSQL + persistance d'états (2 semaines).
- **Sprint 2**: Reprise automatique et résilience des traitements (2 semaines).
- **Sprint 3**: API temps réel + contrat frontend (1-2 semaines).
- **Sprint 4**: Migration UI React (2 semaines).
- **Sprint 5**: Affichage rouge des erreurs dans « Dossiers » + validation persistée (1 semaine).
- **Sprint 6**: Stabilisation, migration finale et mise en production (1-2 semaines).

**Total estimé: 10 à 12 semaines** (selon disponibilité équipe et dette technique découverte).

## 📊 KPIs de succès

- Taux de reprise automatique réussie après crash > 95%.
- 0 perte d'état métier entre redémarrages.
- Temps de propagation backend -> UI < 3 s (p95).
- Réduction des revalidations inutiles > 80%.
- 100% des erreurs critiques visibles en UI avec message actionnable.

## 🚀 Prochaines étapes

1. Valider la direction technique (palette + structure + priorités métier).
2. Produire une maquette V1 de `templates/index.html` (sans toucher au backend).
3. Implémenter en incréments (PR courte par phase), avec capture d'écran à chaque étape.

## 📝 Conclusion

La migration vers une interface React avec une mise à jour en temps réel permettra d'améliorer significativement le dynamisme et l'affichage live des traitements audiobooks. Les sprints proposés offrent un plan clair pour atteindre les objectifs tout en minimisant les risques.
