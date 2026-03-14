# TR001 - Questionnaire de Validation Phase 0 (Kickoff UI v3)

**Date** : 2026-03-14  
**Document source** : PR006-ui_v3_development_phasing.md  
**Phase** : Phase 0 - Kickoff produit & choix des variantes  
**Durée** : 3 jours  
**Statut** : À valider  

---

## 📋 Objectifs de la Validation

Valider les décisions techniques fondamentales pour le démarrage du développement UI v3, en s'assurant que :

1. Les choix technologiques sont cohérents avec les objectifs produit
2. Les livrables de Phase 0 sont clairs et réalisables
3. Les contraintes et principes sont bien compris
4. Les risques sont identifiés et mitigés

---

## 🔍 Questions de Validation

### **Section A - Architecture et Stack Technique**

#### **A1. Stack Backend**
**Question** : La stack imposée (FastAPI + PostgreSQL + asyncpg + triggers) est-elle validée pour les besoins ?

**Options** :
- [X] ✅ **OUI** - Stack cohérente et validée
- [ ] ❌ **NON** - Stack inadaptée ou nécessite ajustements
- [ ] ⚠️ **CONDITIONNEL** - Valide sous conditions précises

**Si NON ou CONDITIONNEL, préciser** :
________________________________________________________________
________________________________________________________________

#### **A2. Principes d'Architecture**
**Question** : Les 3 principes sont-ils acceptés et compris ?

1. **Aucun couplage avec templates Flask historiques**
   - [X] ✅ **Accepté** - Clean break avec l'existant
   - [ ] ❌ **Refusé** - Nécessite compatibilité partielle
   - [ ] ⚠️ **À discuter** - Points de transition à définir

2. **Contrat d'événements versionné dès le départ**
   - [X] ✅ **Accepté** - Versionnement obligatoire
   - [ ] ❌ **Refusé** - Approche plus flexible souhaitée
   - [ ] ⚠️ **À discuter** - Stratégie hybride

3. **Reconnexion WebSocket et idempotence backend obligatoires**
   - [X] ✅ **Accepté** - Robustesse temps réel requise
   - [ ] ❌ **Refusé** - Complexité excessive pour MVP
   - [ ] ⚠️ **À discuter** - Idempotence sélective

**Commentaires** (si applicable) :
________________________________________________________________
________________________________________________________________

---

### **Section B - Décisions Technologiques Frontend**

#### **B1. Choix Framework Frontend**
**Question** : Quel choix pour le framework frontend ?

**Options** :
- [ ] **React + Zustand/Redux Toolkit**
  - Avantages : Écosystème mature, compétences existantes
  - Inconvénients : Bundle size, complexité Redux

- [X] **Svelte + stores**
  - Avantages : Performance, bundle size minimal
  - Inconvénients : Courbe d'apprentissage, écosystème moins mature

- [ ] **AUTRE** (préciser) : ________________________________

**Justification du choix** :
Rapidité et flexibilité__________________________________________
________________________________________________________________

#### **B2. Système de Design**
**Question** : Quel système de design UI ?

**Options** :
- [X] **Tailwind CSS**
  - Avantages : Customisation maximale, performance
  - Inconvénients : CSS à écrire, moins de composants prêts

- [ ] **CoreUI**
  - Avantages : Composants prêts, cohérence visuelle
  - Inconvénients : Moins flexible, dépendance tierce

- [ ] **AUTRE** (préciser) : ________________________________

**Justification du choix** :
________________________________________________________________
________________________________________________________________

#### **B3. Stratégie d'Authentification**
**Question** : La stratégie JWT short-lived + refresh est-elle validée ?

**Options** :
- [X] ✅ **VALIDÉE** - JWT courts + refresh token
- [ ] ❌ **REFUSÉE** - Préférence pour session classique
- [ ] ⚠️ **MODIFIÉE** - JWT avec durée différente

**Si MODIFIÉE, préciser la stratégie** :
________________________________________________________________
________________________________________________________________

---

### **Section C - Livrables et Conventions**

#### **C1. Architecture Decision Records (ADR)**
**Question** : Le format ADR Markdown est-il adapté ?

**Validation** :
- [X] ✅ **OUI** - Format ADR standard suffisant
- [ ] ❌ **NON** - Nécessite format plus structuré
- [ ] ⚠️ **ENRICHIR** - ADR + schémas + diagrammes

**Si NON ou ENRICHIR, préciser** :
________________________________________________________________
________________________________________________________________

#### **C2. Maquettes et Design**
**Question** : Quel niveau de maquettage pour la Phase 0 ?

**Options** :
- [X] **Figma complet** - Écrans détaillés, interactions
- [ ] **Schéma léger** - Wireframes + flux principaux
- [ ] **Paper prototyping** - Croquis simples, itération rapide
- [ ] **AUTRE** (préciser) : ________________________________

#### **C3. Contrat d'Événements JSON**
**Question** : Le format proposé est-il suffisant pour le MVP ?

**Validation du format** :
```json
{
  "schema_version": 1,
  "event_id": "uuid",
  "event_type": "insert|update|delete",
  "entity": "job|packet|...",
  "entity_id": "string",
  "timestamp": "ISO-8601",
  "payload": {}
}
```

- [X] ✅ **SUFFISANT** - Format MVP complet
- [ ] ❌ **INSUFFISANT** - Ajouts requis (préciser) :
  - ____________________________________________________________
  - ____________________________________________________________
- [ ] ⚠️ **TROP COMPLEXE** - Simplifier pour MVP (préciser) :
  - ____________________________________________________________

---

### **Section D - MVP et Périmètre**

#### **D1. Définition MVP**
**Question** : Le MVP défini (écrans + actions + métriques live) est-il correct ?

**Écrans MVP validés** :
- [X] **Tableau de bord** (KPI + statut connexion)
- [X] **Liste jobs/packets** (live updates)
- [X] **Détail job** (timeline événements)
- [X] **Gestion erreurs/notifications**
- [ ] **AUTRE** (préciser) : ________________________________

**Actions requises** :
- [X] **CRUD jobs/packets**
- [X] **Monitoring temps réel**
- [X] **Notifications utilisateur**
- [ ] **AUTRE** (préciser) : ________________________________

**Métriques live requises** :
- [ ] **Statut système** (API, DB, WS)
- [ ] **Performance** (temps réponse, débit)
- [X] **Activité utilisateur** (connexions, actions)
- [ ] **AUTRE** (préciser) : ________________________________

#### **D2. Critères d'Acceptation**
**Question** : Quels sont les critères GO/NO-GO pour la Phase 1 ?

**Critères GO** (cocher tous les applicables) :
- [X] Décisions techniques validées et documentées
- [X] MVP clairement défini et accepté
- [X] Équipe formée aux technologies choisies
- [X] Environnement de développement prêt
- [X] Risques identifiés avec plans de mitigation

**Critères NO-GO** (un seul suffit) :
- [ ] Décisions techniques non convergentes
- [ ] MVP trop ambitieux pour 3 semaines
- [X] Compétences techniques insuffisantes
- [X] Dépendances externes bloquantes

---

### **Section E - Risques et Contraintes**

#### **E1. Risques Identifiés**
**Question** : Quels sont les risques principaux pour cette Phase 0 ?

**Risques techniques** (cocher et évaluer 1-3) :
- [ ] **Complexité WebSocket** : [1-3] ______
- [ ] **Performance PostgreSQL** : [1-3] ______
- [ ] **Courbe d'apprentissage frontend** : [1-3] ______
- [ ] **Intégration temps réel** : [1-3] ______
- [ ] **AUTRE** (préciser) : ________________________________

**Risques projet** (cocher et évaluer 1-3) :
- [ ] **Délais** : [1-3] ______
- [ ] **Ressources** : [1-3] ______
- [ ] **Périmètre creep** : [1-3] ______
- [ ] **AUTRE** (préciser) : ________________________________

#### **E2. Plans de Mitigation**
**Question** : Quelles mitigations sont prévues ?

**Pour chaque risque coché ci-dessus, préciser** :
- **Risque** : ________________________________
- **Mitigation** : ________________________________
- **Plan B** : ________________________________

---

## 📊 Synthèse de Validation

### **Décision Finale**
- [X] ✅ **GO** - Phase 0 validée, passage à Phase 1
- [ ] ❌ **NO-GO** - Phase 0 à revoir
- [ ] ⚠️ **GO CONDITIONNEL** - Sous conditions précises

### **Conditions GO (si applicable)** :
1. __________________________________________________________
2. __________________________________________________________
3. __________________________________________________________

### **Actions NO-GO (si applicable)** :
1. __________________________________________________________
2. __________________________________________________________
3. __________________________________________________________

---

## 🔍 Validation par les Parties Prenantes

### **Signatures requises**

**Lead Technique** :
- Nom : ________________________________
- Date : ________________________________
- Signature : ✅ Validé / ❌ Refusé / ⚠️ Conditionnel

**Lead Produit** :
- Nom : ________________________________
- Date : ________________________________
- Signature : ✅ Validé / ❌ Refusé / ⚠️ Conditionnel

**Architecture** :
- Nom : ________________________________
- Date : ________________________________
- Signature : ✅ Validé / ❌ Refusé / ⚠️ Conditionnel

---

## 📝 Notes Additionnelles

**Commentaires généraux** :
________________________________________________________________
________________________________________________________________
________________________________________________________________

**Décisions alternatives explorées** :
________________________________________________________________
________________________________________________________________
________________________________________________________________

**Points de vigilance pour Phase 1** :
________________________________________________________________
________________________________________________________________
________________________________________________________________

---

## 📋 Checklist de Clôture Phase 0

**Avant de passer à Phase 1** :

- [ ] ADR-001 (architecture v3) créé et validé
- [ ] ADR-002 (choix frontend/design) créé et validé
- [ ] Backlog MVP (user stories + critères) défini
- [ ] Maquettes (Figma/schéma) réalisées
- [ ] RFC contrat événements JSON rédigée
- [ ] Environnement de développement prêt
- [ ] Équipe formée aux technologies choisies
- [ ] Risques documentés avec plans de mitigation

---

**Statut final du questionnaire** :
- [ ] ✅ **COMPLET** - Toutes sections remplies
- [ ] ⚠️ **PARTIEL** - Sections à compléter
- [ ] ❌ **INCOMPLET** - Requiert travail additionnel

---

**Date de validation finale** : ________________________________

**Validateur** : ________________________________

**Statut** : ✅ **VALIDÉ** / ❌ **REJETÉ** / ⚠️ **EN ATTENTE**
