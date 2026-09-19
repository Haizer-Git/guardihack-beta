# Guide de mise à jour ProfileView.vue

## 📦 Installation des dépendances

Assurez-vous que les dépendances suivantes sont installées dans le dossier `frontend`:

```bash
cd frontend
npm install
# ou
npm install apexcharts@^3.50.0 chart.js@^4.5.1 axios vue vue-router
```

## ✨ Nouveautés dans ProfileView.vue

### 1. **Design complet inspiré de profile.html**
- Thème sombre cohérent avec des couleurs personnalisées
- Respect strict des boxes et du layout
- Design RootMe-like pour l'activité récente

### 2. **Gestion des badges**
```javascript
// Affichage:
// - Aucun badge si vide
// - Max 10 badges par page
// - Pagination automatique
```

### 3. **Activité récente**
- Affichage "Aucune activité récente" si vide
- Format: titre | date | points
- Limite: 3 dernières activités

### 4. **Heatmap avec ApexCharts**
- 365 jours de contribution
- Gradient de couleurs (gris → or → orange → rouge)
- Groupement par mois
- Tooltip avec détails

### 5. **Graphiques de performance**

#### Progression (Line Chart)
- 6 derniers mois
- Score total en fonction du temps

#### Catégories (Radar Chart)
- Web, Reverse, Forensic, Crypto, Pwn, OSINT
- Thème doré

#### Difficulté (Bar Chart)
- Facile: vert | Moyen: jaune | Difficile: orange | Insane: rouge

## 🎨 Schéma de couleurs

```
Background:     #1a1a1a (Noir très foncé)
Surfaces:       #333333 (Gris très foncé)
Inner:          #2a2a2a (Gris foncé)
Accent Primary: #d4a500 (Or)
Accent Red:     #ff4444 (Rouge)
Border Light:   #555555
Border Medium:  #444444
```

## 📡 Routes API utilisées

```
GET /api/user/info/me
  → Retourne le profil utilisateur courant

GET /api/user/badges
  → Retourne les badges de l'utilisateur
```

## 🚀 Fonctionnalités

- ✅ Chargement progressif
- ✅ Gestion des erreurs
- ✅ Refresh du profil possible
- ✅ Responsive design
- ✅ Pagination des badges
- ✅ Animations fluides

## 📋 Checklist avant déploiement

- [ ] `npm install` lancé dans `/frontend`
- [ ] ApexCharts ajouté au package.json
- [ ] Pas d'erreurs de console
- [ ] Tous les graphiques s'affichent
- [ ] Heatmap apparaît avec les couleurs correctes
- [ ] Pagination des badges fonctionne
- [ ] Messages "Aucun badge" / "Aucune activité" s'affichent si vide
- [ ] API calls réussies (logs en console)

## 🔧 Configuration

Aucune configuration additionnelle requise. Le composant utilise:
- axios avec baseURL configurée dans main.js
- Chart.js automatiquement
- ApexCharts automatiquement

## 📝 Notes supplémentaires

- L'activité récente est actuellement simulée (à remplacer par l'API)
- Les stats (rank, solveCount, etc.) sont générées aléatoirement (à remplacer par l'API)
- La heatmap utilise 365 jours de données simulées (peut être remplacé par des vraies données du backend)

Pour intégrer les vraies données, modifier les sections:
- `simulateRecentActivity()` 
- `loadProfile()` - section des stats
- `initializeHeatmap()` - génération des données
