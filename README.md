# 🚀 Component Data Processor v2.0

## Architecture Moderne FastAPI + Flask

### 📋 Description

Système de traitement de données de composants YAZAKI avec architecture moderne séparant backend et frontend. Le système permet la sélection dynamique de colonnes de projets et le traitement automatisé de fichiers Excel.

### 🏗️ Architecture

```
Component Data Processor v2.0
├── 🔧 Backend FastAPI (Port 8000)
│   ├── API REST moderne
│   ├── Traitement des fichiers
│   └── Documentation automatique
│
├── 🌐 Frontend Flask (Port 5000)
│   ├── Interface web utilisateur
│   └── Communication avec backend
│
└── 📊 Données
    ├── Master_BOM_Real.xlsx (22 colonnes de projets)
    └── Fichiers d'entrée/sortie
```

### ✨ Fonctionnalités

- ✅ **22 colonnes de projets** détectées automatiquement
- ✅ **Sélection dynamique** de colonnes via interface web
- ✅ **Upload et traitement** de fichiers Excel
- ✅ **API REST complète** avec documentation Swagger
- ✅ **Architecture Backend/Frontend** séparée
- ✅ **Tests d'intégration** automatisés

### 🚀 Démarrage Rapide

#### 1. Installation
```bash
pip install -r requirements.txt
```

#### 2. Démarrage du système
```bash
python START_SYSTEM.py
```

#### 3. Accès aux services
- **Interface web**: http://localhost:5000
- **API Backend**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

### 📊 Utilisation

1. **Sélection de colonne** : Cliquer sur "Charger" pour voir les 22 colonnes
2. **Upload de fichier** : Sélectionner un fichier Excel (.xlsx)
3. **Traitement** : Choisir une colonne de projet et traiter
4. **Résultat** : Télécharger le fichier traité

### 🔧 Fichiers Principaux

| Fichier | Description |
|---------|-------------|
| `START_SYSTEM.py` | 🚀 Démarrage système complet |
| `backend_simple.py` | 🔧 Backend FastAPI |
| `simple_web.py` | 🌐 Frontend Flask |
| `frontend_api_client.py` | 📡 Client API |
| `runner.py` | ⚙️ Processeur principal |
| `config.py` | 🔧 Configuration |
| `Master_BOM_Real.xlsx` | 📊 Master BOM (22 colonnes) |
| `test_complete_system.py` | 🧪 Tests d'intégration |

### 🧪 Tests

```bash
# Test complet du système
python test_complete_system.py
```

### 📚 Documentation

- **Guide d'utilisation** : `GUIDE_UTILISATION_FINAL.md`
- **Documentation technique** : `README_FINAL.md`
- **API Documentation** : http://localhost:8000/docs

### 🎯 Colonnes de Projets Recommandées

Pour projets Ford V710_B2:
- `V710_B2_J74_JOB1+90_YMOK` (35.1% rempli)
- `V710_B2_J74_JOB1+90_YOT-K` (20.4% rempli)
- `V710_B2_J74_JOB1+90_YWTT` (26.2% rempli)

### 🔍 Dépannage

#### Backend non disponible
```bash
python -m uvicorn backend_simple:app --host 0.0.0.0 --port 8000
```

#### Frontend non accessible
```bash
python simple_web.py
```

#### Tests échoués
```bash
# Vérifier les services
curl http://localhost:8000/health
curl http://localhost:5000
```

### 📈 Performances

- **Colonnes détectées** : 22 colonnes (colonnes 2-23)
- **Temps de traitement** : 3-5 secondes par fichier
- **Formats supportés** : .xlsx, .xls
- **Taille max** : 100MB

### 🏆 Avantages

1. **Architecture moderne** : Séparation Backend/Frontend
2. **API REST** : Documentation automatique Swagger
3. **Interface intuitive** : Sélection dynamique de colonnes
4. **Tests automatisés** : Validation d'intégration
5. **Logs détaillés** : Traçabilité complète
6. **Prêt production** : Architecture scalable

---

## 🎉 Système Opérationnel

**Architecture moderne ✅ | Interface intuitive ✅ | API complète ✅**

Le Component Data Processor v2.0 est prêt pour la production avec une architecture professionnelle moderne.
