# 🚀 Guide de démarrage rapide

## Installation et première utilisation

### 1. ⚡ Démarrage ultra-rapide

```bash
# Windows
run setup
run samples
run process Sample_Input_Data.xlsx

# Linux/macOS
./run.sh setup
./run.sh samples
./run.sh process Sample_Input_Data.xlsx

# Ou avec Make
make dev-setup
make process-sample
```

### 2. 🐍 Méthode Python directe

```bash
# Configuration
python runner.py setup

# Créer des exemples
python runner.py samples

# Traiter un fichier
python runner.py process Sample_Input_Data.xlsx

# Ou directement
python main.py Sample_Input_Data.xlsx
```

## 🎯 Commandes essentielles

### Runner principal (`runner.py`)

```bash
# 📊 Informations et statut
python runner.py info          # Infos du projet
python runner.py status        # Statut actuel
python runner.py docs          # Documentation

# 🔧 Configuration
python runner.py setup         # Configuration initiale
python runner.py config list   # Lister les configs
python runner.py config create prod  # Créer config

# 📋 Traitement
python runner.py samples       # Créer exemples
python runner.py process file.xlsx    # Traiter fichier
python runner.py batch "*.xlsx"       # Traitement lot
python runner.py validate file.xlsx   # Validation seule

# 🧪 Tests et maintenance
python runner.py test          # Tests unitaires
python runner.py test --coverage      # Avec couverture
python runner.py clean         # Nettoyage
```

### Scripts de démarrage

```bash
# Windows (run.bat)
run setup                      # Configuration
run samples                    # Créer exemples
run process input.xlsx         # Traiter fichier
run test                       # Tests

# Linux/macOS (run.sh)
./run.sh setup
./run.sh samples
./run.sh process input.xlsx
./run.sh test
```

### Makefile (Linux/macOS)

```bash
make help                      # Aide
make setup                     # Configuration complète
make samples                   # Créer exemples
make test                      # Tests
make process-sample            # Traiter exemple
make clean                     # Nettoyage
```

## 📁 Structure des fichiers

```
📦 component-data-processor/
├── 🚀 Démarrage rapide
│   ├── runner.py              # Runner principal
│   ├── run.bat               # Script Windows
│   ├── run.sh                # Script Linux/macOS
│   └── Makefile              # Commandes Make
├── 
├── 🎯 Application
│   ├── main.py               # Point d'entrée
│   └── src/                  # Code source modulaire
├── 
├── ⚙️ Configuration
│   └── config/
│       ├── default.json      # Configuration par défaut
│       └── production.json   # Config production
├── 
└── 📊 Sorties
    └── output/               # Fichiers générés
```

## 🎨 Exemples d'utilisation

### 1. Premier traitement

```bash
# Créer les fichiers d'exemple
python runner.py samples

# Traiter avec configuration par défaut
python runner.py process Sample_Input_Data.xlsx

# Vérifier les résultats
ls output/
```

### 2. Configuration personnalisée

```bash
# Créer une config personnalisée
python runner.py config create custom

# Éditer config/custom.json selon vos besoins
# Puis traiter avec cette config
python runner.py process input.xlsx --config config/custom.json
```

### 3. Traitement en lot

```bash
# Traiter tous les fichiers Excel d'un dossier
python runner.py batch "data/*.xlsx"

# Avec configuration spécifique
python main.py --batch "*.xlsx" --config config/production.json
```

### 4. Validation avant traitement

```bash
# Valider un fichier sans le traiter
python runner.py validate input.xlsx

# Validation en mode verbeux
python main.py input.xlsx --validate-only --verbose
```

## 🔧 Configuration rapide

### Fichier de configuration JSON

```json
{
  "files": {
    "master_bom_path": "Master_BOM.xlsx",
    "output_dir": "output",
    "backup_enabled": true
  },
  "processing": {
    "required_columns": ["PN", "Project"],
    "convert_to_uppercase": true
  },
  "logging": {
    "level": "INFO",
    "log_to_console": true
  }
}
```

### Variables d'environnement

```bash
# Windows
set COMPONENT_PROCESSOR_MASTER_BOM=path\to\Master_BOM.xlsx
set COMPONENT_PROCESSOR_LOG_LEVEL=DEBUG

# Linux/macOS
export COMPONENT_PROCESSOR_MASTER_BOM="path/to/Master_BOM.xlsx"
export COMPONENT_PROCESSOR_LOG_LEVEL="DEBUG"
```

## 🧪 Tests et validation

```bash
# Tests rapides
python runner.py test

# Tests avec couverture
python runner.py test --coverage

# Test d'un module spécifique
python runner.py test --module test_data_cleaner

# Validation d'un fichier
python runner.py validate Sample_Input_Data.xlsx
```

## 📊 Comprendre les sorties

### Fichiers générés

- **`Update_[date].xlsx`** : Données traitées avec formatage
  - 🟡 Jaune : Composants mis à jour (D→X)
  - 🔴 Rouge : Doublons/inconnus nécessitant attention
  - 🔘 Gris : Composants ignorés (status X)

- **`Clean_Excluded_[date].xlsx`** : Lignes exclues pendant le nettoyage

- **`Processing_Summary_[date].csv`** : Statistiques détaillées

- **`component_processor_[date].log`** : Logs complets

### Statistiques affichées

```
Lignes originales: 25        # Données d'entrée
Lignes nettoyées: 22         # Après nettoyage
Lignes exclues: 3            # Problématiques
Mises à jour D→X: 4          # Composants dépréciés
Doublons ajoutés: 2          # Nécessitent vérification
Inconnus ajoutés: 5          # Nouveaux composants
Ignorés (status X): 1        # Déjà marqués anciens
```

## 🆘 Dépannage rapide

### Problèmes courants

```bash
# Erreur "Module not found"
python runner.py setup        # Réinstaller dépendances

# Fichier Master BOM introuvable
python runner.py config list  # Vérifier config
# Éditer le chemin dans config/default.json

# Erreurs de permissions
# Vérifier les droits d'accès aux fichiers

# Problèmes de format
python runner.py validate input.xlsx  # Valider avant traitement
```

### Obtenir de l'aide

```bash
# Aide générale
python runner.py --help
python main.py --help

# Statut du projet
python runner.py status

# Documentation
python runner.py docs
```

## 🎯 Prochaines étapes

1. **📖 Lire la documentation** : `docs/` pour plus de détails
2. **⚙️ Personnaliser la config** : Adapter `config/default.json`
3. **🔧 Intégrer dans vos workflows** : Utiliser l'API programmatique
4. **🚀 Déployer en production** : Suivre `docs/DEPLOYMENT.md`

---

**🎉 Vous êtes maintenant prêt à utiliser le Component Data Processor !**

Pour plus d'informations :
- 📖 **README.md** : Guide complet
- 🏗️ **docs/ARCHITECTURE.md** : Architecture technique
- 🔧 **docs/API_REFERENCE.md** : Référence API
- 🚀 **docs/DEPLOYMENT.md** : Déploiement production
