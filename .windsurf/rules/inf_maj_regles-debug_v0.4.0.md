# Règles Debug (majeure)

Routine de débogage pour erreurs persistantes ou corrections incomplètes. À utiliser uniquement en cas de blocage.

### DIAGNOSTIC
- Collecter tous les messages d'erreur, logs et symptômes comportementaux
- Ajouter le contexte pertinent des fichiers
- Récupérer l'architecture du projet, le plan et la tâche en cours depuis @memory.mdc

### PROCÉDURE
- En cas d'échec de test, ajouter plus de contexte avec <DIAGNOSTIC> et déboguer efficacement d'abord
- Expliquer les OBSERVATIONS puis les RAISONNEMENTS pour identifier exactement le problème
- Si incertain, obtenir plus d'OBSERVATIONS en ajoutant plus de contexte <DIAGNOSTIC>
- Chercher des patterns similaires résolus ailleurs dans le code
- Présenter la correction avec validation

### ANALYSE CODE
Comprendre l'architecture en analysant les dépendances et les flux de données.

### RAISONNEMENT ÉTAPE PAR ÉTAPE
Penser à toutes les causes possibles : désalignement architectural, défaut de conception, etc.

### PRÉSENTATION RAISONNEMENT
Présenter la correction pour validation.

## Contexte d'utilisation
Appliqué lors du débogage d'erreurs persistantes dans le développement, assurant une approche systématique et complète du diagnostic et de la résolution.

**Version : 0.4.0** | **Catégorie : Informatique/Développement**
