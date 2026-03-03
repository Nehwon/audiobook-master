# Guide d'utilisation de l'outil `sequentialthinking` MCP (majeure)

---
description: Guide pour utiliser efficacement l'outil sequentialthinking MCP pour la résolution de problèmes dynamique et réfléchie.
author: https://github.com/rafaelkallis
version: 1.0
tags: ["mcp", "sequentialthinking", "problem-solving", "workflow-guide", "ai-guidance"]
globs: ["*"] # Pertinent pour toute tâche nécessitant des processus de pensée complexes
---

# Guide d'utilisation de l'outil `sequentialthinking` MCP

## 1. Objectif

Cette règle guide Cline (l'IA) dans l'utilisation efficace de l'outil `sequentialthinking` MCP. Cet outil est conçu pour la résolution de problèmes dynamique et réfléchie, permettant un processus de pensée flexible qui peut s'adapter, évoluer et s'appuyer sur des insights précédents.

## 2. Quand utiliser l'outil `sequentialthinking`

Cline DEVRAIT envisager d'utiliser l'outil `sequentialthinking` lorsqu'il est confronté à des tâches impliquant :

*   **Décomposition complexe de problèmes :** Diviser de gros problèmes multifacettes en étapes plus petites et gérables.
*   **Planification et conception (itérative) :** Architecturer des solutions où le plan pourrait nécessiter une révision à mesure que la compréhension s'approfondit.
*   **Analyse approfondie :** Situations nécessitant une analyse attentive où les hypothèses initiales pourraient être remises en question ou nécessiter une correction de trajectoire.
*   **Portée incertaine :** Problèmes où la portée complète n'est pas immédiatement évidente et nécessite une réflexion exploratoire.
*   **Solutions multi-étapes :** Tâches qui nécessitent intrinsèquement une séquence de pensées ou d'actions interconnectées pour être résolues.
*   **Maintenance du contexte :** Scénarios où maintenir une ligne de pensée cohérente à travers plusieurs étapes est crucial.
*   **Filtrage d'informations :** Lorsqu'il est nécessaire de trier les informations et d'identifier ce qui est pertinent à chaque étape de la réflexion.
*   **Génération et vérification d'hypothèses :** Former et tester des hypothèses dans le cadre du processus de résolution de problèmes.

## 3. Principes fondamentaux pour utiliser `sequentialthinking`

Lors de l'invocation de l'outil `sequentialthinking`, Cline DOIT adhérer aux principes suivants :

*   **Processus de pensée itératif :** Chaque utilisation de l'outil représente une seule "pensée". S'appuyer sur, questionner ou réviser les pensées précédentes dans les appels suivants.
*   **Nombre de pensées dynamique :**
    *   Commencer avec une estimation initiale pour `totalThoughts`.
    *   Être prêt à ajuster `totalThoughts` (à la hausse ou à la baisse) à mesure que le processus de pensée évolue.
    *   Si plus de pensées sont nécessaires que l'estimation initiale, incrémenter `thoughtNumber` au-delà du `totalThoughts` original et mettre à jour `totalThoughts` en conséquence.
*   **Réflexion honnête :**
    *   Exprimer l'incertitude si elle existe.
    *   Marquer explicitement les pensées qui révisent la réflexion précédente en utilisant `isRevision: true` et `revisesThought: <thought_number>`.
    *   Si explorer un chemin alternatif, envisager d'utiliser `branchFromThought` et `branchId` pour suivre les lignes de raisonnement divergentes.
*   **Approche axée sur les hypothèses :**
    *   Générer une `hypothesis` de solution lorsqu'une solution potentielle émerge du processus de pensée.
    *   Vérifier l'`hypothesis` basée sur les étapes précédentes de la chaîne de pensée.
    *   Répéter le processus de pensée (plus de pensées) si l'hypothèse n'est pas satisfaisante.
*   **Filtrage de pertinence :** Ignorer activement ou filtrer les informations qui ne sont pas pertinentes pour la `thought` actuelle ou l'étape du processus de résolution de problèmes.
*   **Clarté dans chaque pensée :** Chaque chaîne `thought` devrait être claire, concise et axée sur un aspect spécifique du problème ou une étape de la raison.
*   **Condition d'achèvement :** Ne définir `nextThoughtNeeded: false` que lorsqu'on est vraiment terminé et qu'une réponse ou solution satisfaisante a été atteinte et vérifiée.

## 4. Paramètres de l'outil `sequentialthinking`

Cline DOIT utiliser correctement les paramètres suivants lors de l'appel de `use_mcp_tool` pour `sequentialthinking` :

*   **`thought` (string, required) :** L'étape de réflexion actuelle. Cela peut être une étape analytique, une question, une révision, une hypothèse, etc.
*   **`nextThoughtNeeded` (boolean, required) :**
    *   `true` : Si plus d'étapes de réflexion sont requises.
    *   `false` : Si le processus de réflexion est terminé et qu'une solution/réponse satisfaisante est atteinte.
*   **`thoughtNumber` (integer, required, min: 1) :** Le numéro séquentiel actuel de la pensée.
*   **`totalThoughts` (integer, required, min: 1) :** Le nombre total *estimé* actuel de pensées nécessaires. Cela peut être ajusté.
*   **`isRevision` (boolean, optional) :** Définir sur `true` si cette pensée révise ou reconsidère une pensée précédente.
*   **`revisesThought` (integer, optional, min: 1) :** Si `isRevision` est true, cela spécifie le `thoughtNumber` de la pensée en cours de révision.
*   **`branchFromThought` (integer, optional, min: 1) :** Si cette pensée représente un point de branchement d'une ligne de pensée précédente, spécifier le `thoughtNumber` à partir duquel elle branche.
*   **`branchId` (string, optional) :** Un identifiant pour la branche actuelle de pensée, si applicable.
*   **`needsMoreThoughts` (boolean, optional) :** Utiliser si `thoughtNumber` a atteint `totalThoughts`, mais que Cline réalise qu'il a besoin de plus de réflexion. Cela signale la nécessité de continuer et potentiellement d'ajuster `totalThoughts`.

## 5. Exemple de workflow (conceptuel)

Cela illustre comment Cline pourrait utiliser l'outil de manière itérative.

**Tâche utilisateur :** "Planifier l'architecture pour une nouvelle fonctionnalité e-commerce : 'Recommandations personnalisées'."

**Processus interne de Cline utilisant `sequentialthinking` :**

1.  **Pensée 1 :**
    *   `thought` : "Approche initiale : Identifier les composants clés pour les recommandations personnalisées. Ils incluent probablement un module de collecte de données, un moteur de recommandation et un module d'affichage."
    *   `nextThoughtNeeded` : true
    *   `thoughtNumber` : 1
    *   `totalThoughts` : 5 (estimation initiale)
2.  **Pensée 2 (L'utilisateur fournit un retour ou Cline réalise quelque chose) :**
    *   `thought` : "Affinement des composants : La collecte de données doit capturer le comportement utilisateur (vues, achats, notations). Le moteur pourrait utiliser le filtrage collaboratif. Le module d'affichage doit s'intégrer aux pages produit et à une section dédiée 'Recommandé pour vous'."
    *   `nextThoughtNeeded` : true
    *   `thoughtNumber` : 2
    *   `totalThoughts` : 5
3.  **Pensée 3 (Considération des alternatives/contraintes) :**
    *   `thought` : "Contrainte : Traitement en temps réel vs. par lots pour les recommandations. Le temps réel offre une meilleure UX mais est plus complexe. Le lot pourrait être un bon MVP pour simplifier."
    *   `nextThoughtNeeded` : true
    *   `thoughtNumber` : 3
    *   `totalThoughts` : 5
4.  **Pensée 4 (Hypothèse) :**
    *   `thought` : "Hypothèse : Un moteur de filtrage collaboratif traité par lots, avec des données collectées à partir de journaux d'interaction utilisateur, affiché sur les pages produit et une section dédiée, est une architecture MVP viable."
    *   `nextThoughtNeeded` : true
    *   `thoughtNumber` : 4
    *   `totalThoughts` : 5
5.  **Pensée 5 (Vérification & réalisation) :**
    *   `thought` : "Vérification : L'hypothèse couvre les aspects clés. Cependant, je n'ai pas considéré le stockage des données pour les profils utilisateur et les journaux d'interaction, ou comment le moteur de recommandation se met à jour. Plus de pensées nécessaires."
    *   `nextThoughtNeeded` : true
    *   `thoughtNumber` : 5
    *   `totalThoughts` : 7 (estimation révisée)
    *   `needsMoreThoughts` : true
6.  **Pensée 6 (Adresse les omissions) :**
    *   `thought` : "Adresse le stockage des données : Une base de données NoSQL (par ex. MongoDB) pourrait convenir pour les profils utilisateur et les journaux d'interaction en raison du schéma flexible. Le moteur de recommandation lirait depuis cela et stockerait son modèle séparément, mis à jour par un travail par lots programmé."
    *   `nextThoughtNeeded` : true
    *   `thoughtNumber` : 6
    *   `totalThoughts` : 7
7.  **Pensée 7 (Finalisation du plan pour MVP) :**
    *   `thought` : "Plan MVP final : 1. Enregistreur d'interaction utilisateur (vers DB NoSQL). 2. Moteur de filtrage collaboratif par lots (lit depuis NoSQL, met à jour le modèle). 3. API pour servir les recommandations. 4. Intégration UI sur les pages produit & section dédiée. Cela semble complet pour un MVP."
    *   `nextThoughtNeeded` : false
    *   `thoughtNumber` : 7
    *   `totalThoughts` : 7

## 6. Rappels critiques pour Cline

*   **NE PAS** utiliser cet outil pour des tâches simples à une étape. Il est pour le raisonnement complexe.
*   **TOUJOURS** s'assurer que `thoughtNumber` s'incrémente correctement.
*   **ÊTRE PRÊT** à ajuster `totalThoughts` à mesure que la compréhension évolue.
*   **SE CONCENTRER** sur la progression vers une solution avec chaque pensée.
*   Si une ligne de pensée devient une impasse, **ÉTAT EXPLICITEMENT** cela dans une `thought` et envisager de réviser une pensée précédente ou de commencer une nouvelle branche.

Ce guide devrait aider Cline à tirer pleinement parti de l'outil `sequentialthinking` MCP.

## Contexte d'utilisation
Utiliser cet outil pour les tâches de résolution de problèmes complexes nécessitant une réflexion itérative et structurée, comme la planification d'architecture logicielle ou l'analyse approfondie de problèmes techniques.

**Version : 0.4.0** | **Catégorie : Communication/IA**
