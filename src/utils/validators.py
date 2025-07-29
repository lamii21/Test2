"""
Validateurs de données pour le Component Data Processor.

Fournit des fonctions de validation pour les données d'entrée,
les formats de fichiers et la cohérence des données.
"""

import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any


class DataValidator:
    """Validateur centralisé pour les données de composants."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialise le validateur.
        
        Args:
            config: Configuration de validation (optionnel)
        """
        self.config = config or self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Retourne la configuration par défaut."""
        return {
            'pn_pattern': r'^[A-Z0-9\-_]+$',
            'max_pn_length': 50,
            'max_project_length': 100,
            'required_columns': ['PN', 'Project'],
            'valid_statuses': ['A', 'D', '0', 'X'],
            'price_min': 0.0,
            'price_max': 10000.0
        }
    
    def validate_part_number(self, pn: str) -> Tuple[bool, str]:
        """
        Valide un numéro de pièce.
        
        Args:
            pn: Numéro de pièce à valider
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not pn or pd.isna(pn):
            return False, "Numéro de pièce manquant"
        
        pn_str = str(pn).strip()
        
        if len(pn_str) == 0:
            return False, "Numéro de pièce vide"
        
        if len(pn_str) > self.config['max_pn_length']:
            return False, f"Numéro de pièce trop long (max: {self.config['max_pn_length']})"
        
        if not re.match(self.config['pn_pattern'], pn_str):
            return False, "Format de numéro de pièce invalide"
        
        return True, ""
    
    def validate_project(self, project: str) -> Tuple[bool, str]:
        """
        Valide un nom de projet.
        
        Args:
            project: Nom de projet à valider
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not project or pd.isna(project):
            return False, "Nom de projet manquant"
        
        project_str = str(project).strip()
        
        if len(project_str) == 0:
            return False, "Nom de projet vide"
        
        if len(project_str) > self.config['max_project_length']:
            return False, f"Nom de projet trop long (max: {self.config['max_project_length']})"
        
        return True, ""
    
    def validate_price(self, price: Any) -> Tuple[bool, str]:
        """
        Valide un prix.
        
        Args:
            price: Prix à valider
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if pd.isna(price):
            return True, ""  # Prix optionnel
        
        try:
            price_float = float(price)
            
            if price_float < self.config['price_min']:
                return False, f"Prix trop bas (min: {self.config['price_min']})"
            
            if price_float > self.config['price_max']:
                return False, f"Prix trop élevé (max: {self.config['price_max']})"
            
            return True, ""
        except (ValueError, TypeError):
            return False, "Format de prix invalide"
    
    def validate_status(self, status: str) -> Tuple[bool, str]:
        """
        Valide un statut de composant.
        
        Args:
            status: Statut à valider
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if pd.isna(status):
            return True, ""  # Statut NaN est valide (composant inconnu)
        
        status_str = str(status).strip().upper()
        
        if status_str in self.config['valid_statuses']:
            return True, ""
        
        return False, f"Statut invalide. Valeurs acceptées: {self.config['valid_statuses']}"
    
    def validate_dataframe_structure(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valide la structure d'un DataFrame.
        
        Args:
            df: DataFrame à valider
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Vérifier que le DataFrame n'est pas vide
        if df.empty:
            errors.append("DataFrame vide")
            return False, errors
        
        # Vérifier les colonnes requises
        missing_columns = set(self.config['required_columns']) - set(df.columns)
        if missing_columns:
            errors.append(f"Colonnes manquantes: {list(missing_columns)}")
        
        # Vérifier les types de données
        for col in self.config['required_columns']:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    errors.append(f"Colonne '{col}': {null_count} valeurs manquantes")
        
        return len(errors) == 0, errors
    
    def validate_row(self, row: pd.Series) -> Tuple[bool, List[str]]:
        """
        Valide une ligne de données.
        
        Args:
            row: Ligne à valider
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Valider le numéro de pièce
        pn_valid, pn_error = self.validate_part_number(row.get('PN'))
        if not pn_valid:
            errors.append(f"PN: {pn_error}")
        
        # Valider le projet
        project_valid, project_error = self.validate_project(row.get('Project'))
        if not project_valid:
            errors.append(f"Project: {project_error}")
        
        # Valider le prix si présent
        if 'Price' in row:
            price_valid, price_error = self.validate_price(row.get('Price'))
            if not price_valid:
                errors.append(f"Price: {price_error}")
        
        # Valider le statut si présent
        if 'Status' in row:
            status_valid, status_error = self.validate_status(row.get('Status'))
            if not status_valid:
                errors.append(f"Status: {status_error}")
        
        return len(errors) == 0, errors
    
    def validate_file_format(self, file_path: str) -> Tuple[bool, str]:
        """
        Valide le format d'un fichier.
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Tuple (is_valid, error_message)
        """
        path = Path(file_path)
        
        if not path.exists():
            return False, "Fichier inexistant"
        
        if not path.is_file():
            return False, "Chemin ne pointe pas vers un fichier"
        
        if path.suffix.lower() not in ['.xlsx', '.xls']:
            return False, "Format de fichier non supporté (Excel requis)"
        
        # Vérifier la taille du fichier
        file_size = path.stat().st_size
        max_size = 100 * 1024 * 1024  # 100 MB
        if file_size > max_size:
            return False, f"Fichier trop volumineux (max: {max_size // (1024*1024)} MB)"
        
        return True, ""
    
    def validate_excel_content(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Valide le contenu d'un fichier Excel.
        
        Args:
            file_path: Chemin du fichier Excel
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Lire le fichier Excel
            df = pd.read_excel(file_path)
            
            # Valider la structure
            structure_valid, structure_errors = self.validate_dataframe_structure(df)
            if not structure_valid:
                errors.extend(structure_errors)
            
            # Valider un échantillon de lignes
            sample_size = min(10, len(df))
            for idx in range(sample_size):
                row_valid, row_errors = self.validate_row(df.iloc[idx])
                if not row_valid:
                    errors.append(f"Ligne {idx + 1}: {'; '.join(row_errors)}")
            
        except Exception as e:
            errors.append(f"Erreur lors de la lecture du fichier: {str(e)}")
        
        return len(errors) == 0, errors
    
    def get_validation_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Génère un résumé de validation pour un DataFrame.
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec les statistiques de validation
        """
        summary = {
            'total_rows': len(df),
            'valid_rows': 0,
            'invalid_rows': 0,
            'missing_pn': 0,
            'missing_project': 0,
            'invalid_prices': 0,
            'invalid_statuses': 0
        }
        
        for idx, row in df.iterrows():
            row_valid, _ = self.validate_row(row)
            
            if row_valid:
                summary['valid_rows'] += 1
            else:
                summary['invalid_rows'] += 1
            
            # Compter les erreurs spécifiques
            if not self.validate_part_number(row.get('PN'))[0]:
                summary['missing_pn'] += 1
            
            if not self.validate_project(row.get('Project'))[0]:
                summary['missing_project'] += 1
            
            if 'Price' in row and not self.validate_price(row.get('Price'))[0]:
                summary['invalid_prices'] += 1
            
            if 'Status' in row and not self.validate_status(row.get('Status'))[0]:
                summary['invalid_statuses'] += 1
        
        return summary
