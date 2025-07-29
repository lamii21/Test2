# Référence API - Component Data Processor

## Vue d'ensemble

Cette documentation décrit l'API publique du Component Data Processor, permettant l'intégration dans d'autres applications ou l'extension des fonctionnalités.

## Module principal

### ComponentDataProcessor

```python
from src.component_processor.processor import ComponentDataProcessor

processor = ComponentDataProcessor(config_file="config.json")
```

#### Méthodes principales

##### `process_file(input_file_path: str) -> bool`

Traite un fichier d'entrée complet.

**Paramètres:**
- `input_file_path` (str): Chemin vers le fichier Excel d'entrée

**Retour:**
- `bool`: True si le traitement a réussi, False sinon

**Exemple:**
```python
success = processor.process_file("input_data.xlsx")
if success:
    print("Traitement réussi")
```

##### `process_multiple_files(file_paths: List[str]) -> Dict[str, bool]`

Traite plusieurs fichiers en lot.

**Paramètres:**
- `file_paths` (List[str]): Liste des chemins de fichiers

**Retour:**
- `Dict[str, bool]`: Dictionnaire {fichier: succès}

**Exemple:**
```python
files = ["file1.xlsx", "file2.xlsx"]
results = processor.process_multiple_files(files)
```

##### `get_global_statistics() -> Dict[str, Any]`

Retourne les statistiques globales de traitement.

**Retour:**
- `Dict[str, Any]`: Statistiques détaillées

## Gestionnaires de données

### DataCleaner

```python
from src.data_handlers.data_cleaner import DataCleaner

cleaner = DataCleaner(config, logger)
```

#### Méthodes principales

##### `clean_dataframe(df: pd.DataFrame) -> pd.DataFrame`

Nettoie un DataFrame selon les règles configurées.

**Paramètres:**
- `df` (pd.DataFrame): DataFrame à nettoyer

**Retour:**
- `pd.DataFrame`: DataFrame nettoyé

##### `get_excluded_rows_dataframe() -> pd.DataFrame`

Retourne les lignes exclues pendant le nettoyage.

##### `get_cleaning_statistics() -> Dict[str, Any]`

Retourne les statistiques de nettoyage.

### LookupProcessor

```python
from src.data_handlers.lookup_processor import LookupProcessor

processor = LookupProcessor(logger)
```

#### Méthodes principales

##### `perform_lookup(input_df: pd.DataFrame, master_bom: pd.DataFrame) -> pd.DataFrame`

Effectue le lookup entre données d'entrée et Master BOM.

##### `process_lookup_results(df: pd.DataFrame, master_bom: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]`

Traite les résultats selon la logique métier.

**Retour:**
- `Tuple[pd.DataFrame, pd.DataFrame]`: (DataFrame traité, Master BOM mis à jour)

### ExcelHandler

```python
from src.data_handlers.excel_handler import ExcelHandler

handler = ExcelHandler(logger)
```

#### Méthodes principales

##### `read_excel_file(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame`

Lit un fichier Excel.

##### `write_formatted_excel(df: pd.DataFrame, file_path: str, sheet_name: str = "Updated_Data") -> bool`

Écrit un DataFrame avec formatage avancé.

##### `export_multiple_sheets(data_dict: Dict[str, pd.DataFrame], file_path: str) -> bool`

Exporte plusieurs DataFrames dans un fichier multi-feuilles.

## Utilitaires

### Logger

```python
from src.utils.logger import get_logger

logger = get_logger("MonModule", "INFO")
```

#### Méthodes principales

##### `info(message: str)`, `warning(message: str)`, `error(message: str)`

Méthodes de logging standard.

##### `log_processing_start(file_path: str, total_rows: int)`

Log spécialisé pour le début de traitement.

##### `log_summary(summary: dict)`

Log un résumé des opérations.

### DataValidator

```python
from src.utils.validators import DataValidator

validator = DataValidator(config)
```

#### Méthodes principales

##### `validate_part_number(pn: str) -> Tuple[bool, str]`

Valide un numéro de pièce.

**Retour:**
- `Tuple[bool, str]`: (is_valid, error_message)

##### `validate_dataframe_structure(df: pd.DataFrame) -> Tuple[bool, List[str]]`

Valide la structure d'un DataFrame.

##### `validate_excel_content(file_path: str) -> Tuple[bool, List[str]]`

Valide le contenu d'un fichier Excel.

### FileManager

```python
from src.utils.file_manager import FileManager

manager = FileManager("output")
```

#### Méthodes principales

##### `generate_timestamped_filename(base_name: str, extension: str = ".xlsx") -> str`

Génère un nom de fichier avec timestamp.

##### `backup_file(file_path: Union[str, Path]) -> Optional[Path]`

Crée une sauvegarde d'un fichier.

##### `clean_old_files(directory: Union[str, Path], days_old: int = 30) -> int`

Nettoie les anciens fichiers.

## Configuration

### ConfigManager

```python
from src.component_processor.config_manager import ConfigManager

config_manager = ConfigManager("config.json")
```

#### Méthodes principales

##### `get(section: str, key: Optional[str] = None, default: Any = None) -> Any`

Récupère une valeur de configuration.

##### `get_processing_config() -> ProcessingConfig`

Retourne la configuration de traitement typée.

##### `save_config(file_path: str, format: str = 'json')`

Sauvegarde la configuration actuelle.

### Classes de configuration

#### ProcessingConfig

```python
@dataclass
class ProcessingConfig:
    required_columns: List[str]
    text_columns: List[str]
    convert_to_uppercase: bool
    remove_non_ascii: bool
    trim_whitespace: bool
    normalize_spaces: bool
    remove_empty_rows: bool
```

#### FileConfig

```python
@dataclass
class FileConfig:
    master_bom_path: str
    output_dir: str
    backup_enabled: bool
    cleanup_old_files: bool
    cleanup_days: int
```

## Exemples d'utilisation

### Traitement simple

```python
from src.component_processor.processor import ComponentDataProcessor

# Initialiser le processeur
processor = ComponentDataProcessor()

# Traiter un fichier
success = processor.process_file("input.xlsx")

if success:
    print("Traitement terminé avec succès")
    stats = processor.get_global_statistics()
    print(f"Lignes traitées: {stats['total_rows_processed']}")
```

### Traitement avec configuration personnalisée

```python
# Créer une configuration personnalisée
config = {
    'processing': {
        'required_columns': ['PN', 'Project'],
        'convert_to_uppercase': True
    },
    'files': {
        'master_bom_path': 'custom_bom.xlsx',
        'output_dir': 'custom_output'
    }
}

# Sauvegarder la configuration
import json
with open('custom_config.json', 'w') as f:
    json.dump(config, f)

# Utiliser la configuration
processor = ComponentDataProcessor('custom_config.json')
```

### Nettoyage de données standalone

```python
from src.data_handlers.data_cleaner import DataCleaner
import pandas as pd

# Charger des données
df = pd.read_excel("raw_data.xlsx")

# Configurer le nettoyeur
config = {
    'required_columns': ['PN', 'Project'],
    'convert_to_uppercase': True
}

cleaner = DataCleaner(config)

# Nettoyer les données
cleaned_df = cleaner.clean_dataframe(df)

# Obtenir les statistiques
stats = cleaner.get_cleaning_statistics()
print(f"Lignes exclues: {stats['excluded_rows']}")
```

### Validation de fichiers

```python
from src.utils.validators import DataValidator

validator = DataValidator()

# Valider un fichier
is_valid, errors = validator.validate_excel_content("input.xlsx")

if not is_valid:
    print("Erreurs de validation:")
    for error in errors:
        print(f"- {error}")
```

### Gestion avancée d'Excel

```python
from src.data_handlers.excel_handler import ExcelHandler
import pandas as pd

handler = ExcelHandler()

# Lire avec formatage
df = handler.read_excel_file("input.xlsx")

# Ajouter des colonnes de traitement
df['Action'] = 'Updated'
df['Notes'] = 'Traitement automatique'

# Écrire avec formatage
handler.write_formatted_excel(df, "output_formatted.xlsx")

# Export multi-feuilles
data_dict = {
    'Main_Data': df,
    'Summary': summary_df,
    'Excluded': excluded_df
}
handler.export_multiple_sheets(data_dict, "complete_report.xlsx")
```

## Gestion des erreurs

### Exceptions personnalisées

```python
class ComponentProcessorError(Exception):
    """Exception de base pour le Component Data Processor."""
    pass

class ValidationError(ComponentProcessorError):
    """Erreur de validation des données."""
    pass

class ConfigurationError(ComponentProcessorError):
    """Erreur de configuration."""
    pass
```

### Gestion des erreurs dans l'API

```python
try:
    processor = ComponentDataProcessor("config.json")
    success = processor.process_file("input.xlsx")
except ConfigurationError as e:
    print(f"Erreur de configuration: {e}")
except ValidationError as e:
    print(f"Erreur de validation: {e}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
```

## Intégration

### Utilisation en tant que bibliothèque

```python
# setup.py pour distribution
from setuptools import setup, find_packages

setup(
    name="component-data-processor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "openpyxl>=3.0.9",
        "numpy>=1.21.0"
    ]
)
```

### API REST (exemple d'extension)

```python
from flask import Flask, request, jsonify
from src.component_processor.processor import ComponentDataProcessor

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_file():
    file = request.files['file']
    
    # Sauvegarder temporairement
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)
    
    # Traiter
    processor = ComponentDataProcessor()
    success = processor.process_file(temp_path)
    
    return jsonify({
        'success': success,
        'statistics': processor.get_global_statistics()
    })
```
