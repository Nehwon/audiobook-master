# Audiobook Master

> Plateforme de traitement audio avec deux architectures disponibles

## 🎯 Vue d'Ensemble

Audiobook Master est une application complète de traitement audio qui existe en deux versions :

- **📖 Version 2 (V2)** : Architecture Flask avec templates Jinja2
- **🚀 Version 3 (V3)** : Architecture moderne FastAPI + Svelte + WebSocket

---

## 📚 Documentation

### 📖 Version 2 (Stable)
[**README_V2.md**](README_V2.md) - Documentation complète de la version stable

- Architecture Flask + SQLite
- Templates Jinja2
- Interface web classique
- Scripts de traitement audio

### 🚀 Version 3 (Alpha)
[**README_V3.md**](README_V3.md) - Documentation de la nouvelle architecture

- Backend FastAPI + PostgreSQL
- Frontend Svelte + Tailwind CSS
- WebSocket temps réel
- API REST complète
- Interface moderne et responsive

---

## 🎯 Choisir une Version

### Utiliser V2 si :
- ✅ Vous avez besoin d'une version stable et éprouvée
- ✅ Vous préférez une interface web classique
- ✅ Vous voulez une configuration simple
- ✅ Vous utilisez l'application existante

### Utiliser V3 si :
- ✅ Vous voulez une architecture moderne
- ✅ Vous avez besoin d'une API REST complète
- ✅ Vous voulez une interface SPA responsive
- ✅ Vous avez besoin du temps réel (WebSocket)
- ✅ Vous développez de nouvelles fonctionnalités

---

## 🚀 Démarrage Rapide

### Version 2
```bash
# Cloner et utiliser la branche main
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master
# Voir README_V2.md pour les instructions
```

### Version 3
```bash
# Cloner et utiliser la branche V3.0.0a
git clone https://github.com/Nehwon/audiobook-master.git
cd audiobook-master
git checkout V3.0.0a
# Voir README_V3.md pour les instructions
```

---

## 🏗️ Comparaison des Architectures

| Caractéristique | V2 (Flask) | V3 (FastAPI + Svelte) |
|----------------|-------------|------------------------|
| **Backend** | Flask | FastAPI |
| **Frontend** | Jinja2 Templates | Svelte SPA |
| **Base de données** | SQLite | PostgreSQL |
| **API** | Routes Flask | REST API |
| **Temps réel** | Non | WebSocket |
| **Responsive** | Limité | Mobile-first |
| **Documentation** | Markdown | Swagger/OpenAPI |
| **Tests** | Basiques | Complets |
| **Déploiement** | Simple | Docker |

---

## 📁 Structure du Proôt

```
audiobook-master/
├── README.md              # Ce fichier
├── README_V2.md           # Documentation V2
├── README_V3.md           # Documentation V3
├── v2/                    # Code de la version 2
│   ├── web/              # Application Flask
│   ├── core/             # Scripts de traitement
│   └── persistence/      # Base de données SQLite
├── v3/                    # Code de la version 3
│   ├── backend/          # FastAPI application
│   ├── frontend/         # SvelteKit application
│   └── docker-compose.yml # Orchestration Docker
├── docs/                  # Documentation partagée
├── LICENSE               # License AGPL-3.0
└── CHANGELOG.md          # Historique des changements
```

---

## 🔄 Migration

### Guide de Migration V2 → V3
1. Sauvegarder vos données V2
2. Installer les dépendances V3
3. Exporter/importer les données dans PostgreSQL
4. Configurer les variables d'environnement
5. Tester la nouvelle interface

Voir [README_V3.md](README_V3.md) pour les détails complets.

---

## 🤝 Contribuer

### Pour V2
- Forker le projet
- Travailler sur la branche `main`
- Créer des PR vers `main`

### Pour V3
- Forker le projet
- Travailler sur la branche `V3.0.0a`
- Créer des PR vers `V3.0.0a`

---

## 📊 État des Versions

| Version | Statut | Branche | Documentation |
|---------|--------|---------|---------------|
| V2 | ✅ Stable | `main` | [README_V2.md](README_V2.md) |
| V3 | 🚀 Alpha | `V3.0.0a` | [README_V3.md](README_V3.md) |

---

## 📄 License

Ce projet est sous license AGPL-3.0. Voir [LICENSE](LICENSE) pour les détails.

---

## 🆘 Support

### Issues et Discussions
- **GitHub Issues** : [Signaler un problème](https://github.com/Nehwon/audiobook-master/issues)
- **GitHub Discussions** : [Discussions](https://github.com/Nehwon/audiobook-master/discussions)

### Documentation
- **V2** : Voir [README_V2.md](README_V2.md)
- **V3** : Voir [README_V3.md](README_V3.md)
- **Architecture** : Voir dossier [docs/](docs/)

---

**Audiobook Master** - La puissance du traitement audio, deux approches pour tous les besoins 🎧✨
