# 🚀 Component Data Processor v2.0

## Architecture Moderne FastAPI + Flask

### 📋 Vue d'ensemble

Ce projet implémente un système de traitement de données de composants YAZAKI avec une architecture moderne séparant backend et frontend, inspirée du projet [ETL-Automated-Tool](https://github.com/Storbiic/ETL-Automated-Tool).

### 🏗️ Architecture

```
Component Data Processor v2.0
├── 🔧 Backend FastAPI (Port 8000)
│   ├── API REST moderne
│   ├── Traitement des fichiers
│   ├── Gestion des colonnes de projets
│   └── Documentation automatique
│
├── 🌐 Frontend Flask (Port 5000)
│   ├── Interface web utilisateur
│   ├── Upload de fichiers
│   ├── Sélection de colonnes
│   └── Communication avec backend
│
└── 📊 Données
    ├── Master_BOM_Real.xlsx (22 colonnes de projets)
    ├── Fichiers d'entrée utilisateur
    └── Fichiers de sortie traités
```

### ✨ Fonctionnalités

#### 🎯 Fonctionnalités Principales
- ✅ **Sélection dynamique de colonnes de projets** (colonnes 2-23 du Master BOM)
- ✅ **Upload et traitement de fichiers Excel**
- ✅ **Lookup automatique avec Master BOM**
- ✅ **Nettoyage et validation des données**
- ✅ **Interface web intuitive**
- ✅ **API REST complète**

#### 🔧 Fonctionnalités Techniques
- ✅ **Architecture Backend/Frontend séparée**
- ✅ **Documentation API automatique (Swagger)**
- ✅ **Gestion d'erreurs robuste**
- ✅ **Logs détaillés**
- ✅ **CORS configuré**
- ✅ **Surveillance des processus**

### 🚀 Démarrage Rapide

#### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

#### 2. Démarrage du système complet
```bash
python start_complete_system.py
```

#### 3. Accès aux services
- **Interface web**: http://localhost:5000
- **API Backend**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

### 📡 API Endpoints

#### Backend FastAPI (Port 8000)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | État du système |
| `/project-columns` | GET | Colonnes de projets disponibles |
| `/upload` | POST | Upload de fichier |
| `/process` | POST | Traitement de fichier |
| `/docs` | GET | Documentation Swagger |

#### Frontend Flask (Port 5000)

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Interface principale |
| `/upload` | POST | Upload et traitement |
| `/api/project-columns` | GET | Proxy vers backend |

### 📊 Utilisation

#### 1. Sélection de colonne de projet
1. Ouvrir l'interface web: http://localhost:5000
2. Cliquer sur "Charger" pour voir les colonnes disponibles
3. Sélectionner la colonne de projet appropriée

#### 2. Traitement de fichier
1. Sélectionner un fichier Excel (.xlsx)
2. Choisir la colonne de projet (optionnel)
3. Cliquer sur "Traiter le fichier"
4. Télécharger le résultat

#### 3. Colonnes de projets recommandées
Pour un projet `FORD_J74_V710_B2_PP_YOTK_00000`:
- `V710_B2_J74_JOB1+90_YMOK` (35.1% rempli)
- `V710_B2_J74_JOB1+90_YOT-K` (20.4% rempli)
- `V710_B2_J74_JOB1+90_YWTT` (26.2% rempli)

### 🔧 Configuration

#### Variables d'environnement
```bash
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=5000

# Traitement
PROCESSING_TIMEOUT=300
MASTER_BOM_PATH=Master_BOM_Real.xlsx
```

### 📁 Structure du projet

```
Test2/
├── 🚀 start_complete_system.py    # Démarrage système complet
├── 🔧 backend_simple.py           # Backend FastAPI
├── 🌐 simple_web.py               # Frontend Flask
├── 📡 frontend_api_client.py      # Client API
├── ⚙️  runner.py                   # Processeur principal
├── 📊 Master_BOM_Real.xlsx        # Master BOM (22 colonnes)
├── 📋 requirements.txt            # Dépendances Python
├── 📚 README_FINAL.md             # Cette documentation
└── 📁 src/                        # Code source
    ├── data_handlers/
    ├── processors/
    └── utils/
```

### 🧪 Tests

#### Test d'intégration automatique
Le système effectue automatiquement des tests d'intégration au démarrage:
- ✅ Santé du backend
- ✅ Communication frontend ↔ backend
- ✅ Détection des colonnes de projets

#### Tests manuels
```bash
# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:5000/api/project-columns

# Test upload (via interface web)
```

### 🔍 Dépannage

#### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Changer les ports dans la configuration
   BACKEND_PORT=8001
   FRONTEND_PORT=5001
   ```

2. **Master BOM non trouvé**
   ```bash
   # Vérifier le chemin
   ls -la Master_BOM_Real.xlsx
   ```

3. **Erreur de dépendances**
   ```bash
   # Réinstaller les dépendances
   pip install -r requirements.txt --force-reinstall
   ```

### 📈 Performances

- **Colonnes de projets**: 22 colonnes détectées (colonnes 2-23)
- **Temps de traitement**: ~3-5 secondes par fichier
- **Formats supportés**: .xlsx, .xls
- **Taille max fichier**: 100MB

### 🎯 Prochaines améliorations

- [ ] Cache Redis pour les performances
- [ ] Base de données pour l'historique
- [ ] Interface utilisateur améliorée
- [ ] API d'authentification
- [ ] Traitement par lots
- [ ] Notifications en temps réel

### 📞 Support

Pour toute question ou problème:
1. Vérifier les logs dans la console
2. Consulter la documentation API: http://localhost:8000/docs
3. Vérifier l'état des services: http://localhost:8000/health

---

**🎉 Système finalisé et opérationnel !**
Architecture moderne ✅ | Interface intuitive ✅ | API complète ✅
