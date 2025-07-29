"""
Gestionnaire de configuration pour le Component Data Processor.

Centralise la gestion de la configuration avec support pour
différents environnements et validation des paramètres.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from ..utils.logger import Logger


@dataclass
class ProcessingConfig:
    """Configuration pour le traitement des données."""
    required_columns: List[str]
    text_columns: List[str]
    convert_to_uppercase: bool
    remove_non_ascii: bool
    trim_whitespace: bool
    normalize_spaces: bool
    remove_empty_rows: bool


@dataclass
class FileConfig:
    """Configuration pour les fichiers."""
    master_bom_path: str
    output_dir: str
    backup_enabled: bool
    cleanup_old_files: bool
    cleanup_days: int


@dataclass
class ValidationConfig:
    """Configuration pour la validation."""
    pn_pattern: str
    max_pn_length: int
    max_project_length: int
    price_min: float
    price_max: float
    valid_statuses: List[str]


@dataclass
class LoggingConfig:
    """Configuration pour le logging."""
    level: str
    log_to_console: bool
    log_to_file: bool
    log_file_pattern: str


@dataclass
class ExcelConfig:
    """Configuration pour Excel."""
    highlight_colors: Dict[str, str]
    auto_adjust_columns: bool
    add_summary_sheet: bool
    freeze_header: bool


class ConfigManager:
    """Gestionnaire centralisé de configuration."""
    
    def __init__(self, config_file: Optional[str] = None, logger: Optional[Logger] = None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_file: Chemin vers le fichier de configuration (optionnel)
            logger: Instance de logger (optionnel)
        """
        self.logger = logger or Logger("ConfigManager")
        self.config_file = config_file
        self._config = self._load_configuration()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Charge la configuration depuis différentes sources."""
        # Configuration par défaut
        config = self._get_default_config()
        
        # Charger depuis le fichier si spécifié
        if self.config_file and Path(self.config_file).exists():
            try:
                file_config = self._load_from_file(self.config_file)
                config = self._merge_configs(config, file_config)
                self.logger.info(f"Configuration chargée depuis: {self.config_file}")
            except Exception as e:
                self.logger.warning(f"Erreur lors du chargement du fichier de config: {e}")
        
        # Appliquer les variables d'environnement
        config = self._apply_environment_overrides(config)
        
        # Valider la configuration
        self._validate_config(config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retourne la configuration par défaut."""
        return {
            'processing': asdict(ProcessingConfig(
                required_columns=['PN', 'Project'],
                text_columns=['PN', 'Project', 'Supplier', 'Description'],
                convert_to_uppercase=True,
                remove_non_ascii=True,
                trim_whitespace=True,
                normalize_spaces=True,
                remove_empty_rows=True
            )),
            'files': asdict(FileConfig(
                master_bom_path='Master_BOM.xlsx',
                output_dir='output',
                backup_enabled=True,
                cleanup_old_files=False,
                cleanup_days=30
            )),
            'validation': asdict(ValidationConfig(
                pn_pattern=r'^[A-Z0-9\-_]+$',
                max_pn_length=50,
                max_project_length=100,
                price_min=0.0,
                price_max=10000.0,
                valid_statuses=['A', 'D', '0', 'X']
            )),
            'logging': asdict(LoggingConfig(
                level='INFO',
                log_to_console=True,
                log_to_file=True,
                log_file_pattern='component_processor_{timestamp}.log'
            )),
            'excel': asdict(ExcelConfig(
                highlight_colors={
                    'duplicate': 'FFCCCC',
                    'updated': 'FFFFCC',
                    'skipped': 'E6E6E6',
                    'error': 'FF9999',
                    'header': '4472C4'
                },
                auto_adjust_columns=True,
                add_summary_sheet=True,
                freeze_header=True
            ))
        }
    
    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Charge la configuration depuis un fichier."""
        path = Path(file_path)
        
        if path.suffix.lower() == '.json':
            return self._load_json_config(file_path)
        elif path.suffix.lower() == '.py':
            return self._load_python_config(file_path)
        else:
            raise ValueError(f"Format de fichier de configuration non supporté: {path.suffix}")
    
    def _load_json_config(self, file_path: str) -> Dict[str, Any]:
        """Charge la configuration depuis un fichier JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_python_config(self, file_path: str) -> Dict[str, Any]:
        """Charge la configuration depuis un fichier Python."""
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("config", file_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Extraire les variables de configuration
        config = {}
        for attr_name in dir(config_module):
            if not attr_name.startswith('_'):
                attr_value = getattr(config_module, attr_name)
                if not callable(attr_value):
                    config[attr_name.lower()] = attr_value
        
        return self._restructure_python_config(config)
    
    def _restructure_python_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Restructure la configuration Python en format standard."""
        structured = {
            'processing': {},
            'files': {},
            'validation': {},
            'logging': {},
            'excel': {}
        }
        
        # Mapping des variables vers les sections
        mappings = {
            'processing': ['required_columns', 'text_columns', 'convert_to_uppercase', 
                          'remove_non_ascii', 'trim_whitespace', 'normalize_spaces', 'remove_empty_rows'],
            'files': ['master_bom_path', 'output_dir', 'backup_enabled', 'cleanup_old_files', 'cleanup_days'],
            'validation': ['pn_pattern', 'max_pn_length', 'max_project_length', 
                          'price_min', 'price_max', 'valid_statuses'],
            'logging': ['log_level', 'log_to_console', 'log_to_file', 'log_file_pattern'],
            'excel': ['highlight_colors', 'auto_adjust_columns', 'add_summary_sheet', 'freeze_header']
        }
        
        for section, keys in mappings.items():
            for key in keys:
                if key in config:
                    structured[section][key] = config[key]
        
        return structured
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Fusionne deux configurations."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Applique les surcharges depuis les variables d'environnement."""
        env_mappings = {
            'COMPONENT_PROCESSOR_MASTER_BOM': ('files', 'master_bom_path'),
            'COMPONENT_PROCESSOR_OUTPUT_DIR': ('files', 'output_dir'),
            'COMPONENT_PROCESSOR_LOG_LEVEL': ('logging', 'level'),
            'COMPONENT_PROCESSOR_BACKUP': ('files', 'backup_enabled'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                if section not in config:
                    config[section] = {}
                
                # Convertir les valeurs booléennes
                if key in ['backup_enabled', 'log_to_console', 'log_to_file']:
                    config[section][key] = env_value.lower() in ('true', '1', 'yes', 'on')
                else:
                    config[section][key] = env_value
                
                self.logger.info(f"Configuration surchargée par variable d'environnement: {env_var}")
        
        return config
    
    def _validate_config(self, config: Dict[str, Any]):
        """Valide la configuration."""
        errors = []
        
        # Valider les chemins de fichiers
        if 'files' in config:
            master_bom_path = config['files'].get('master_bom_path')
            if master_bom_path and not Path(master_bom_path).exists():
                errors.append(f"Fichier Master BOM introuvable: {master_bom_path}")
        
        # Valider les colonnes requises
        if 'processing' in config:
            required_cols = config['processing'].get('required_columns', [])
            if not required_cols:
                errors.append("Aucune colonne requise définie")
        
        # Valider les niveaux de logging
        if 'logging' in config:
            log_level = config['logging'].get('level', 'INFO')
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if log_level.upper() not in valid_levels:
                errors.append(f"Niveau de logging invalide: {log_level}")
        
        if errors:
            error_msg = "Erreurs de configuration:\n" + "\n".join(f"- {error}" for error in errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            section: Section de configuration
            key: Clé spécifique (optionnel)
            default: Valeur par défaut
            
        Returns:
            Valeur de configuration
        """
        if section not in self._config:
            return default
        
        if key is None:
            return self._config[section]
        
        return self._config[section].get(key, default)
    
    def get_processing_config(self) -> ProcessingConfig:
        """Retourne la configuration de traitement."""
        config_dict = self.get('processing', default={})
        return ProcessingConfig(**config_dict)
    
    def get_file_config(self) -> FileConfig:
        """Retourne la configuration des fichiers."""
        config_dict = self.get('files', default={})
        return FileConfig(**config_dict)
    
    def get_validation_config(self) -> ValidationConfig:
        """Retourne la configuration de validation."""
        config_dict = self.get('validation', default={})
        return ValidationConfig(**config_dict)
    
    def get_logging_config(self) -> LoggingConfig:
        """Retourne la configuration de logging."""
        config_dict = self.get('logging', default={})
        return LoggingConfig(**config_dict)
    
    def get_excel_config(self) -> ExcelConfig:
        """Retourne la configuration Excel."""
        config_dict = self.get('excel', default={})
        return ExcelConfig(**config_dict)
    
    def save_config(self, file_path: str, format: str = 'json'):
        """
        Sauvegarde la configuration actuelle.
        
        Args:
            file_path: Chemin du fichier de sortie
            format: Format de sortie ('json' ou 'python')
        """
        try:
            if format.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Format non supporté: {format}")
            
            self.logger.info(f"Configuration sauvegardée: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            raise
    
    def reload(self):
        """Recharge la configuration."""
        self._config = self._load_configuration()
        self.logger.info("Configuration rechargée")
    
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la configuration."""
        return {
            'master_bom_path': self.get('files', 'master_bom_path'),
            'output_dir': self.get('files', 'output_dir'),
            'log_level': self.get('logging', 'level'),
            'required_columns': self.get('processing', 'required_columns'),
            'backup_enabled': self.get('files', 'backup_enabled'),
            'config_file': self.config_file
        }
