# 📌 Plan d'action pour la migration React + Vite + PostgreSQL

## 🎯 Objectifs

1. **Migrer l'interface vers React + Vite** pour une expérience utilisateur plus dynamique et réactive.
2. **Passer sur PostgreSQL** pour persister les états d'exécution et de validation, permettre la reprise automatique après incident/redémarrage, et afficher les erreurs de manière claire dans la zone **Dossiers**.
3. **Simplifier l'interface** en supprimant la page "Traitements" si possible.
4. **Rendre le système de plugins efficace** avec un guide complet de développement des plugins.
5. **Rendre les pages plus attractives et efficaces** avec une refonte UI/UX.

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
