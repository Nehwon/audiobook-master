# Utilisation de l'Outil new_task (majeure)

Ce guide fournit des instructions obligatoires pour décomposer efficacement les tâches complexes et implémenter un processus de transmission fluide entre les tâches. Vous devez suivre ces directives pour assurer la continuité, la préservation du contexte et l'efficacité de l'achèvement des tâches.

## Surveillance de la Fenêtre de Contexte

Vous devez surveiller l'utilisation de la fenêtre de contexte affichée dans les détails d'environnement. Lorsque l'utilisation dépasse 50% de la fenêtre de contexte disponible, vous devez initier une transmission de tâche en utilisant l'outil `new_task`.

## Décomposition des Tâches en Mode Plan

Le Mode Plan est spécifiquement conçu pour analyser les tâches complexes et les décomposer en sous-tâches gérables. En Mode Plan, vous devez :

1. Analyser initialement la tâche pour comprendre pleinement la portée
2. Décomposer stratégiquement la tâche en sous-tâches logiques et discrètes
3. Créer une feuille de route des tâches claire avec dépendances
4. Obtenir l'approbation de l'utilisateur avant de passer en Mode Act

## Processus d'Implémentation et de Transmission

Lors de l'implémentation, vous devez :

1. Vous concentrer sur l'achèvement complet de la sous-tâche actuelle
2. Identifier les points d'achèvement naturels (tâche terminée, point logique, temps dépassé, portée étendue, fenêtre de contexte >50%)
3. Initier le processus de transmission en utilisant `ask_followup_question` puis `new_task` si approuvé
4. Inclure un contexte détaillé dans la nouvelle tâche : travail terminé, état actuel, prochaines étapes, informations de référence

## Meilleures Pratiques pour Transmissions Efficaces

- Maintenir la continuité avec terminologie cohérente et références aux décisions précédentes
- Préserver le contexte avec extraits de code pertinents et résumés de discussions
- Définir des actions suivantes claires et prioritiser les tâches restantes
- Documenter les hypothèses et identifier les besoins d'entrée utilisateur
- Optimiser pour la reprise avec instructions claires et résumé rapide

## Contexte d'utilisation

À utiliser obligatoirement lors de tâches complexes nécessitant décomposition, surveillance de la fenêtre de contexte dépassant 50%, ou lorsque la session doit être interrompue. Assure des transitions fluides et préserve l'élan du projet.

**Version : 0.4.0** | **Catégorie : Communication/IA**
