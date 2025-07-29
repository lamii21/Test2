# Component Data Processor

Une application Python modulaire qui automatise le traitement et la mise à jour des données de composants basées sur des fichiers Excel. Cet outil effectue le nettoyage des données, le traitement XLOOKUP contre un Master BOM, et génère des sorties mises à jour avec des rapports complets.

## 🚀 Fonctionnalités

- **Nettoyage automatique des données**: Supprime les lignes vides, nettoie les espaces, normalise le formatage
- **Traitement XLOOKUP**: Compare les données d'entrée avec la référence Master BOM
- **Logique basée sur les statuts**: Gère différents statuts de composants (D, 0, X, NaN) avec des actions spécifiques
- **Sortie Excel formatée**: Génère des fichiers Excel avec mise en surbrillance et commentaires
- **Logging complet**: Logs détaillés et rapports de résumé
- **Architecture modulaire**: Facile à maintenir et étendre
- **Tests unitaires**: Couverture de tests complète
- **Configuration flexible**: Support JSON et variables d'environnement

## 📋 Business Logic

### Step 1: Data Collection
- Input: Filtered Excel spreadsheet received manually (from supplier/collaborator)
- Contains component data with Part Number (PN) and Project fields

### Step 2: Data Cleaning
- Remove empty rows or rows with missing critical values (PN, Project)
- Trim whitespaces and standardize formatting
- Normalize special characters
- Export excluded rows to `Clean_Excluded_[date].xlsx`

### Step 3: Lookup + Processing Logic
For each row, performs XLOOKUP between PN + Project and Master BOM:

- **Status = "D" (Deprecated)**: Update Master BOM status to "X", add comment
- **Status = "0" (Duplicate)**: Add new row for manual verification
- **Status = "NaN" (Unknown)**: Add new row as potential new entry
- **Status = "X" (Old)**: Skip processing

### Step 4: Output Generation
- Save updated Excel as `Update_[YYYY-MM-DD].xlsx`
- Generate summary report (CSV/PDF)
- Optional: Email updated file to recipients

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup
1. Clone or download the project files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Core Dependencies
```
pandas>=1.5.0
numpy>=1.21.0
openpyxl>=3.0.9
xlsxwriter>=3.0.3
```

## 📁 Structure du projet

```
component-data-processor/
├── src/                          # Code source principal
│   ├── component_processor/      # Module principal
│   │   ├── processor.py          # Orchestrateur principal
│   │   └── config_manager.py     # Gestionnaire de configuration
│   ├── data_handlers/            # Gestionnaires de données
│   │   ├── excel_handler.py      # Gestion des fichiers Excel
│   │   ├── data_cleaner.py       # Nettoyage des données
│   │   └── lookup_processor.py   # Traitement des lookups
│   └── utils/                    # Utilitaires
│       ├── logger.py             # Système de logging
│       ├── file_manager.py       # Gestion des fichiers
│       └── validators.py         # Validation des données
├── tests/                        # Tests unitaires
├── docs/                         # Documentation technique
├── config/                       # Fichiers de configuration
├── examples/                     # Exemples et fichiers de test
├── main.py                       # Point d'entrée principal
├── requirements.txt              # Dépendances Python
└── output/                       # Fichiers générés
    ├── Update_[date].xlsx
    ├── Clean_Excluded_[date].xlsx
    ├── Processing_Summary_[date].csv
    └── component_processor_[date].log
```

## 🚀 Démarrage rapide

### 1. Générer des fichiers d'exemple
```bash
# Créer des fichiers d'exemple
python main.py --create-samples
```

### 2. Traiter un fichier
```bash
# Traiter un fichier unique
python main.py Sample_Input_Data.xlsx

# Avec configuration personnalisée
python main.py Sample_Input_Data.xlsx --config config/custom.json

# Traitement en lot
python main.py --batch "*.xlsx"

# Mode validation seulement
python main.py Sample_Input_Data.xlsx --validate-only
```

### 3. Vérifier les résultats
- Données mises à jour: `output/Update_[date].xlsx`
- Log de traitement: `component_processor_[date].log`
- Rapport de résumé: `output/Processing_Summary_[date].csv`
- Lignes exclues: `output/Clean_Excluded_[date].xlsx`

## ⚙️ Configuration

### Configuration JSON

Créer un fichier `config/custom.json`:

```json
{
  "files": {
    "master_bom_path": "Master_BOM.xlsx",
    "output_dir": "output",
    "backup_enabled": true
  },
  "processing": {
    "required_columns": ["PN", "Project"],
    "convert_to_uppercase": true,
    "remove_non_ascii": true
  },
  "logging": {
    "level": "INFO",
    "log_to_console": true,
    "log_to_file": true
  },
  "validation": {
    "max_pn_length": 50,
    "valid_statuses": ["A", "D", "0", "X"]
  }
}
```

### Variables d'environnement

```bash
export COMPONENT_PROCESSOR_MASTER_BOM="path/to/Master_BOM.xlsx"
export COMPONENT_PROCESSOR_OUTPUT_DIR="path/to/output"
export COMPONENT_PROCESSOR_LOG_LEVEL="DEBUG"
```

## 📊 Output Files

### Main Output (`Update_[date].xlsx`)
- Original data with processing results
- Color-coded rows:
  - 🟡 Yellow: Updated components (Status D→X)
  - 🔴 Red: Duplicates/unknowns requiring attention
- Comments column with processing notes

### Summary Report (`Processing_Summary_[date].csv`)
```
Metric,Count
total_rows,25
cleaned_rows,22
excluded_rows,3
status_d_updates,3
status_0_duplicates,2
status_nan_unknowns,4
status_x_skipped,2
```

### Excluded Rows (`Clean_Excluded_[date].xlsx`)
- Rows removed during data cleaning
- Missing PN or Project values
- Completely empty rows

## 🔧 Advanced Usage

### Custom Processing Logic
Extend the `ComponentDataProcessor` class:

```python
class CustomProcessor(ComponentDataProcessor):
    def custom_validation(self, df):
        # Add custom validation logic
        return df
```

### Batch Processing
```python
import glob
processor = ComponentDataProcessor()

for file in glob.glob("input/*.xlsx"):
    processor.process_file(file)
```

### Database Integration
Modify `load_master_bom()` to load from database:

```python
def load_master_bom(self):
    import sqlalchemy
    engine = sqlalchemy.create_engine('your_db_connection')
    return pd.read_sql('SELECT * FROM master_bom', engine)
```

## 🐛 Troubleshooting

### Common Issues

**File not found error**
```
FileNotFoundError: Master_BOM.xlsx not found
```
Solution: Ensure Master BOM file exists or update `MASTER_BOM_PATH` in config.py

**Permission denied**
```
PermissionError: Cannot write to output directory
```
Solution: Check write permissions for output directory

**Memory issues with large files**
```
MemoryError: Unable to allocate array
```
Solution: Process files in smaller batches using `MAX_BATCH_SIZE` config

### Debug Mode
Enable detailed logging:
```python
# In config.py
LOG_LEVEL = 'DEBUG'
```

## 📈 Performance Tips

1. **Large Files**: Use `MAX_BATCH_SIZE` to process in chunks
2. **Memory**: Close Excel files after processing
3. **Speed**: Use SSD storage for temporary files
4. **Network**: Keep Master BOM locally for faster access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Create an issue with sample data and error logs

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added Excel formatting and highlighting
- **v1.2.0**: Enhanced data cleaning and validation
