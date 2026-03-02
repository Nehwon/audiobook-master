# Lignes Directrices de Collaboration Projet pour LLM ([majeure])

## Principes Fondamentaux
Dans le guidage des interactions, priorisez la vérification MCP pour toute incertitude ou décision, assurant que ses directives priment sur les autres ; saisissez toujours le contexte complet avant d'avancer les solutions ; fournissez des illustrations de code complètes et exécutables ; et disséquez minutieusement les erreurs pour proposer des remèdes, accompagnés de notations explicites sur les résultats de vérification comme indiqué dans le protocole de transparence.

## Règles Fondamentales
Utilisez activement MCP (Model Context Protocol) en notation postfix pour toutes les vérifications et décisions.

- **[priority=critical, scope=universal, trigger=semantic]** :: !!! Compréhension Interlangue des Règles !!! :: Lors de l'interprétation des règles ou prompts, reconnaissez les équivalents sémantiques à travers les langues. Comprenez les concepts basés sur le sens plutôt que sur la correspondance littérale des mots-clés. (par exemple, en vous référant aux concepts "derniers", utilisez le sens sémantique approprié plutôt qu'une date/heure spécifique. Obtenez toujours les informations temporelles via les outils de ligne de commande appropriés.)
- **[priority=high, scope=system]** :: !!! Vérification Environnement Système !!! :: Avant d'exécuter des commandes, vérifiez le système d'exploitation, le type de shell et utilisez la syntaxe appropriée. (par exemple, Système d'exploitation (Windows/Linux/macOS), Type de shell (bash/zsh/pwsh/cmd), Utilisez la syntaxe de commande appropriée pour l'environnement)
- **[priority=high, scope=universal, trigger=experimentation]** :: !!! Pensée Expérimentale !!! :: Lors du débogage d'issues techniques complexes, résistez à l'envie de conclure prématurément basé sur des hypothèses initiales. Au lieu de cela, testez systématiquement toutes les hypothèses via une expérimentation contrôlée, assurant que chaque conclusion est validée empiriquement plutôt qu'assumée théoriquement.

## Langage de Communication
Pour faciliter une collaboration fluide dans ce projet, la sélection du langage est contextuelle. Le chinois simplifié soutient des échanges directs et intuitifs entre l'utilisateur et le LLM, tandis que l'anglais assure la précision et l'interopérabilité pour les éléments de dépôt partagés entre équipes techniques. Cette approche minimise les frais de traduction dans les scénarios interactifs et s'aligne avec les conventions internationales dans les sorties documentées.

- Utilisez le chinois simplifié pour toutes les interactions utilisateur-LLM, telles que les réponses aux requêtes, explications et dialogues conversationnels.
- Utilisez l'anglais pour les artefacts liés au dépôt, incluant :
  - Messages de commit Git (par exemple, adhérer au format Conventional Commits).
  - Fichiers texte trackés par Git (par exemple, README.md ou fichiers de configuration).
  - Documentation projet pour collaboration externe (par exemple, spécifications API ou guides contributeurs).

## Convention de Commit Git
Les messages de commit Git sont en anglais. Utilisez la règle `Conventional Commits 1.0.0`, voir le lien <https://www.conventionalcommits.org/en/v1.0.0/>.

```template
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- Référence : https://www.conventionalcommits.org/en/v1.0.0/
- Types courants : feat, fix, docs, style, refactor, test, chore

## Convention de Fichier Code
Ajoutez un commentaire de chemin relatif sur la première ligne. (par exemple, `# src/utils/helper.py`, `// src/components/Header.jsx`.)

Pour les fichiers avec exigences de première ligne spéciales (par exemple, shebang), utilisez la deuxième ligne :
```bash
#!/bin/bash
# scripts/deploy.sh
```

## Action
1. Commencez simple, puis grandissez. Commencez avec le cas d'usage le plus simple et augmentez la complexité étape par étape.
2. Test modulaire. Testez la fonctionnalité après que chaque étape soit complétée.
3. État d'abord. Assurez-vous que la conception de l'état est saine ; les changements ultérieurs sont coûteux.
4. Intégration progressive. Faites fonctionner le flux de base avant d'ajouter des fonctionnalités avancées.

## Style de Texte
- Le problème fondamental de la communication est de reproduire à un point un message sélectionné à un autre.
- Rendez votre contribution aussi informative que requis ; pas plus que requis. Évitez l'ambiguïté. Soyez bref. Soyez ordonné.
- Omettez les mots inutiles.
- La perfection est atteinte non pas quand il n'y a rien de plus à ajouter, mais quand il n'y a rien de moins à retirer.
- Ne multipliez pas les entités au-delà de la nécessité.

## Contexte d'utilisation
Cette règle s'applique aux lignes directrices générales de collaboration projet avec les LLM, intégrant des principes de développement, conventions de code et meilleures pratiques de communication pour assurer une productivité optimale.

**Version : 0.4.0** | **Catégorie : Informatique/Développement**
