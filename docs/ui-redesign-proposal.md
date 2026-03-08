# Proposition de refonte UI/UX (style dashboard professionnel)

## Objectif
Aligner l'interface web de l'application avec un rendu **dashboard moderne** : lisible, hiérarchisé, efficace pour l'exploitation quotidienne, avec une couleur mieux utilisée (sans surcharge visuelle).

## Principes directeurs
1. **Lisibilité d'abord** : contraste élevé, typo cohérente, densité maîtrisée.
2. **Hiérarchie claire** : informations critiques visibles en premier (santé, files, erreurs).
3. **Actions rapides** : CTA regroupées et stables (scan, traitement, upload, refresh).
4. **Feedback explicite** : statuts, progression, erreurs et succès normalisés.
5. **Cohérence** : mêmes composants, mêmes espacements, mêmes patterns sur toutes les pages.

## Direction visuelle proposée

### 1) Structure globale
- **Barre latérale gauche fixe** (navigation principale) avec icône + libellé.
- **Top bar** : titre de section, recherche/filtre, statut global du service, actions rapides.
- **Contenu central en grille** de cartes (KPI + panneaux fonctionnels).
- **Zone secondaire** pour tableaux détaillés et journaux temps réel.

### 2) Palette et identité
- Fond principal : gris très clair neutre.
- Cartes : blanc avec bordure subtile + ombre légère.
- Couleur primaire (accent) : bleu/violet sobre (ex. `#3B82F6` ou `#4F46E5`).
- Couleurs d'état :
  - Succès : vert (`#16A34A`)
  - Alerte : ambre (`#D97706`)
  - Erreur : rouge (`#DC2626`)
  - Info : bleu (`#2563EB`)

### 3) Typographie et densité
- Titres sections 18–22px, sous-sections 14–16px, corps 13–14px.
- Espacement vertical régulier (échelle 4/8/12/16/24).
- Limiter les blocs trop « pleins » : préférer des cartes compactes mais respirantes.

## Proposition d'architecture écran (V1)

### A. En-tête Dashboard
- **KPI cards (ligne 1)** :
  - Dossiers détectés
  - Jobs en cours
  - Jobs en erreur
  - Uploads en attente
- Chaque carte contient : valeur principale, delta (si utile), mini indicateur visuel.

### B. Zone opérationnelle
- **Colonne gauche** : actions principales (scanner, lancer traitement, valider sélection, extraire).
- **Colonne centre** : pipeline (En attente → En cours → Terminé → À revoir) avec compteurs.
- **Colonne droite** : santé intégrations (Audiobookshelf OK/KO, dernier sync, latence).

### C. Zone listes détaillées
- Tableaux unifiés avec : tri, recherche locale, pagination légère.
- États vides travaillés (« Aucun élément », call-to-action clair).
- Badges de statut homogènes (couleur + icône + texte).

### D. Journal & observabilité
- Panneau repliable « Activité récente » (logs simplifiés).
- Niveau de détail ajustable (Info / Debug).

## Composants UI à normaliser
- Boutons : primaire, secondaire, danger, ghost.
- Inputs : tailles et marges standard.
- Cartes : header + contenu + footer optionnel.
- Badges de statut : success/warn/error/info.
- Barres de progression : déterministe/indéterminée.
- Toasts : succès/alerte/erreur avec action éventuelle.

## Plan d'implémentation recommandé (sans rupture)

### Phase 1 — Fondation visuelle
- Introduire des **design tokens CSS** (couleurs, radius, spacing, shadows, typo).
- Uniformiser les boutons, champs, cartes et tableaux.
- Revoir l'espacement global et les alignements.

### Phase 2 — Layout dashboard
- Mettre en place layout 3 zones : sidebar, topbar, contenu.
- Repositionner les sections actuelles dans des cartes de dashboard.
- Ajouter un bloc KPI en haut.

### Phase 3 — Expérience opérationnelle
- Clarifier le flux de traitement (pipeline visuel + actions groupées).
- Harmoniser les statuts (couleur, wording, icônes).
- Ajouter recherche/filtre simple sur les listes critiques.

### Phase 4 — Finitions pro
- États vides, skeleton loading, focus clavier, hover states.
- Accessibilité (contraste AA, labels, navigation clavier).
- Micro-interactions légères (pas d'animations agressives).

## Critères de succès
- Temps pour trouver une action clé réduit (scan, traitement, upload).
- Moins d'ambiguïté sur l'état système (où ça bloque ? quoi faire ensuite ?).
- Interface perçue comme « plus pro » et stable par les utilisateurs.

## Proposition concrète de prochaine étape
1. Valider ensemble cette direction (palette + structure + priorités métier).
2. Produire une **maquette V1** de `templates/index.html` (sans toucher au backend).
3. Implémenter en incréments (PR courte par phase), avec capture d'écran à chaque étape.
