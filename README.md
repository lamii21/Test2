# Component Data Processor

Un système de traitement de données de composants avec interface web et CLI, optimisé pour les données Yazaki avec lookup VLOOKUP-style.

## 🚀 Démarrage rapide

### Installation
```bash
pip install -r requirements.txt
```

### Utilisation

#### Interface Web (Recommandé)
```bash
python simple_web.py
```
Puis ouvrez http://localhost:5000

#### Ligne de commande
```bash
# Créer des exemples
python runner.py samples

# Traiter un fichier
python runner.py process votre_fichier.xlsx

# Voir le statut
python runner.py status
```

## 📊 Fonctionnalités principales

### 🎯 **Lookup VLOOKUP-style**
- Recherche simple par PN (numéro de pièce)
- Colonne Status ajoutée automatiquement
- Gestion des doublons (premier trouvé)
- Statistiques de mapping détaillées

### 🔄 **Mapping intelligent des colonnes**
- **"YAZAKI PN"** → **"PN"** (numéro de pièce)
- **"BOM ASL FILTER"** → **"Project"** (nom du projet)
- **"Item Description"** → **"Description"**
- **"Manufacturer"** → **"Supplier"**

### 📈 **4 statuts de composants**
- **X** : Ancien (ignoré, gris)
- **D** : Déprécié (à traiter, jaune)  
- **0** : Doublon (à vérifier, rouge)
- **NaN** : Nouveau (à ajouter, bleu)

### 🌐 **Interface web complète**
- Upload par glisser-déposer
- Traitement en temps réel
- Téléchargement des résultats
- Création d'exemples intégrée

## 📁 Structure du projet

```
├── src/                    # Code source principal
│   ├── component_processor/   # Processeur principal
│   ├── data_handlers/         # Gestionnaires de données
│   └── utils/                 # Utilitaires
├── frontend/              # Interface web
│   ├── templates/            # Templates HTML
│   ├── static/              # CSS/JS
│   └── uploads/             # Fichiers uploadés
├── config/               # Configuration
├── output/               # Fichiers de sortie
├── main.py              # Point d'entrée CLI
├── runner.py            # Interface CLI simplifiée
├── simple_web.py        # Serveur web
├── Master_BOM.xlsx      # Master BOM de référence
└── Sample_Input_Data.xlsx   # Données d'exemple
```

## 🎯 Workflow typique

1. **Créer des exemples** : `python runner.py samples`
2. **Remplacer Master_BOM.xlsx** par votre Master BOM réel
3. **Traiter vos données** : Interface web ou CLI
4. **Récupérer les résultats** : Fichiers Excel formatés avec statuts

## 📋 Format des données

### Fichier d'entrée attendu
- **YAZAKI PN** : Numéros de pièces Yazaki
- **BOM ASL FILTER** : Nom du projet
- **Item Description** : Description des composants
- **Manufacturer** : Fournisseur

### Master BOM requis
- **PN** : Numéros de pièces
- **Project** : Nom du projet
- **Status** : X, D, 0, ou vide
- **Description, Supplier, Price** : Informations additionnelles

## 🎨 Résultats du traitement

### Fichiers générés
- **Update_YYYY-MM-DD.xlsx** : Vos données avec statuts
- **Master_BOM_Updated_YYYY-MM-DD.xlsx** : Master BOM mis à jour
- **Processing_Summary_YYYY-MM-DD.csv** : Rapport détaillé

### KPIs affichés
- Total Records
- Status 'X' (Ancien)
- Status 'D' (Déprécié)
- Status '0' (Doublon)
- Not Found (NaN)

## 📖 Documentation

Voir `QUICKSTART.md` pour un guide détaillé d'utilisation.

## 🔧 Configuration

Le système utilise les fichiers de configuration dans `config/`:
- `default.json` : Configuration par défaut
- `production.json` : Configuration de production

## 🧪 Tests

```bash
cd tests
python run_tests.py
```

## 📝 Logs

Les logs sont générés automatiquement dans le répertoire racine avec le format :
`component_processor_YYYY-MM-DD.log`

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request
