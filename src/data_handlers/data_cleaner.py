"""
Nettoyeur de données pour le Component Data Processor.

Fournit des fonctionnalités pour nettoyer, normaliser et valider
les données d'entrée selon les règles métier définies.
"""

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple, Optional, Any

from ..utils.logger import Logger
from ..utils.validators import DataValidator


class DataCleaner:
    """Nettoyeur centralisé pour les données de composants."""
    
    def __init__(self, config: Optional[Dict] = None, logger: Optional[Logger] = None):
        """
        Initialise le nettoyeur de données.
        
        Args:
            config: Configuration de nettoyage (optionnel)
            logger: Instance de logger (optionnel)
        """
        self.logger = logger or Logger("DataCleaner")
        self.config = config or self._get_default_config()
        self.validator = DataValidator()
        
        # Statistiques de nettoyage
        self.cleaning_stats = {
            'original_rows': 0,
            'cleaned_rows': 0,
            'excluded_rows': 0,
            'normalized_values': 0,
            'trimmed_values': 0,
            'case_corrections': 0
        }
        
        # Lignes exclues pour rapport
        self.excluded_rows = []
    
    def _get_default_config(self) -> Dict:
        """Retourne la configuration par défaut."""
        return {
            'required_columns': ['PN', 'Project'],
            'text_columns': ['PN', 'Project', 'Supplier', 'Description'],
            'convert_to_uppercase': True,
            'remove_non_ascii': True,
            'trim_whitespace': True,
            'normalize_spaces': True,
            'remove_empty_rows': True
        }
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie un DataFrame complet selon les règles définies.
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame nettoyé
        """
        self.logger.info("Début du nettoyage des données")
        
        # Réinitialiser les statistiques
        self._reset_stats()
        self.cleaning_stats['original_rows'] = len(df)
        
        # Créer une copie pour éviter de modifier l'original
        cleaned_df = df.copy()
        
        # Étape 1: Supprimer les lignes complètement vides
        if self.config['remove_empty_rows']:
            cleaned_df = self._remove_empty_rows(cleaned_df)
        
        # Étape 2: Identifier et exclure les lignes avec valeurs critiques manquantes
        cleaned_df = self._handle_missing_critical_values(cleaned_df)
        
        # Étape 3: Nettoyer les colonnes texte
        if self.config['text_columns']:
            cleaned_df = self._clean_text_columns(cleaned_df)
        
        # Étape 4: Normaliser les formats
        cleaned_df = self._normalize_formats(cleaned_df)
        
        # Étape 5: Validation finale
        cleaned_df = self._final_validation(cleaned_df)
        
        # Mettre à jour les statistiques finales
        self.cleaning_stats['cleaned_rows'] = len(cleaned_df)
        self.cleaning_stats['excluded_rows'] = (
            self.cleaning_stats['original_rows'] - self.cleaning_stats['cleaned_rows']
        )
        
        self._log_cleaning_summary()
        
        return cleaned_df
    
    def _reset_stats(self):
        """Réinitialise les statistiques de nettoyage."""
        for key in self.cleaning_stats:
            if key not in ['original_rows']:
                self.cleaning_stats[key] = 0
        self.excluded_rows = []
    
    def _remove_empty_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Supprime les lignes complètement vides."""
        before_count = len(df)
        df_cleaned = df.dropna(how='all')
        after_count = len(df_cleaned)
        
        if before_count > after_count:
            self.logger.info(f"Suppression de {before_count - after_count} lignes vides")
        
        return df_cleaned
    
    def _handle_missing_critical_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gère les lignes avec des valeurs critiques manquantes."""
        required_cols = self.config['required_columns']
        
        # Identifier les lignes avec valeurs critiques manquantes
        missing_mask = df[required_cols].isna().any(axis=1)
        
        if missing_mask.any():
            # Sauvegarder les lignes exclues
            excluded_df = df[missing_mask].copy()
            excluded_df['exclusion_reason'] = 'Valeurs critiques manquantes'
            self.excluded_rows.extend(excluded_df.to_dict('records'))
            
            # Supprimer les lignes avec valeurs manquantes
            df_cleaned = df[~missing_mask].copy()
            
            excluded_count = missing_mask.sum()
            self.logger.info(f"Exclusion de {excluded_count} lignes avec valeurs critiques manquantes")
            
            return df_cleaned
        
        return df
    
    def _clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les colonnes texte."""
        text_cols = [col for col in self.config['text_columns'] if col in df.columns]
        
        for col in text_cols:
            self.logger.debug(f"Nettoyage de la colonne: {col}")
            
            # Convertir en string et gérer les NaN
            df[col] = df[col].astype(str)
            df[col] = df[col].replace('nan', '')
            
            # Trim whitespace
            if self.config['trim_whitespace']:
                original_values = df[col].copy()
                df[col] = df[col].str.strip()
                self.cleaning_stats['trimmed_values'] += (original_values != df[col]).sum()
            
            # Normaliser les espaces multiples
            if self.config['normalize_spaces']:
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            
            # Convertir en majuscules
            if self.config['convert_to_uppercase']:
                original_values = df[col].copy()
                df[col] = df[col].str.upper()
                self.cleaning_stats['case_corrections'] += (original_values != df[col]).sum()
            
            # Supprimer les caractères non-ASCII
            if self.config['remove_non_ascii']:
                original_values = df[col].copy()
                df[col] = df[col].apply(self._normalize_text)
                self.cleaning_stats['normalized_values'] += (original_values != df[col]).sum()
        
        return df
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalise un texte en supprimant les caractères non-ASCII.
        
        Args:
            text: Texte à normaliser
            
        Returns:
            Texte normalisé
        """
        if pd.isna(text) or text == 'nan' or text == '':
            return ''
        
        # Convertir en string et supprimer les caractères non-ASCII
        text_str = str(text)
        normalized = text_str.encode('ascii', 'ignore').decode('ascii')
        
        # Supprimer les espaces supplémentaires
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _normalize_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise les formats de données spécifiques."""
        
        # Normaliser les prix
        if 'Price' in df.columns:
            df = self._normalize_prices(df)
        
        # Normaliser les statuts
        if 'Status' in df.columns:
            df = self._normalize_status(df)
        
        return df
    
    def _normalize_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise la colonne des prix."""
        try:
            # Convertir en numérique, forcer les erreurs à NaN
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            
            # Arrondir à 2 décimales
            df['Price'] = df['Price'].round(2)
            
            self.logger.debug("Normalisation des prix terminée")
            
        except Exception as e:
            self.logger.warning(f"Erreur lors de la normalisation des prix: {e}")
        
        return df
    
    def _normalize_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise la colonne des statuts."""
        try:
            # Convertir en string et nettoyer
            df['Status'] = df['Status'].astype(str).str.strip().str.upper()
            
            # Remplacer 'NAN' par NaN réel
            df['Status'] = df['Status'].replace('NAN', np.nan)
            
            self.logger.debug("Normalisation des statuts terminée")
            
        except Exception as e:
            self.logger.warning(f"Erreur lors de la normalisation des statuts: {e}")
        
        return df
    
    def _final_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Effectue une validation finale et exclut les lignes invalides."""
        invalid_rows = []
        valid_indices = []
        
        for idx, row in df.iterrows():
            is_valid, errors = self.validator.validate_row(row)
            
            if is_valid:
                valid_indices.append(idx)
            else:
                # Ajouter aux lignes exclues
                excluded_row = row.to_dict()
                excluded_row['exclusion_reason'] = '; '.join(errors)
                invalid_rows.append(excluded_row)
        
        if invalid_rows:
            self.excluded_rows.extend(invalid_rows)
            self.logger.info(f"Exclusion de {len(invalid_rows)} lignes lors de la validation finale")
        
        return df.loc[valid_indices].copy()
    
    def _log_cleaning_summary(self):
        """Log un résumé du nettoyage."""
        self.logger.info("=== RÉSUMÉ DU NETTOYAGE ===")
        for key, value in self.cleaning_stats.items():
            self.logger.info(f"{key.replace('_', ' ').title()}: {value}")
        self.logger.info("=" * 30)
    
    def get_excluded_rows_dataframe(self) -> pd.DataFrame:
        """
        Retourne un DataFrame avec les lignes exclues.
        
        Returns:
            DataFrame des lignes exclues
        """
        if not self.excluded_rows:
            return pd.DataFrame()
        
        return pd.DataFrame(self.excluded_rows)
    
    def get_cleaning_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de nettoyage.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        return self.cleaning_stats.copy()
    
    def validate_before_cleaning(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valide un DataFrame avant le nettoyage.
        
        Args:
            df: DataFrame à valider
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        return self.validator.validate_dataframe_structure(df)
    
    def clean_single_value(self, value: Any, column_type: str = 'text') -> Any:
        """
        Nettoie une valeur individuelle.
        
        Args:
            value: Valeur à nettoyer
            column_type: Type de colonne ('text', 'price', 'status')
            
        Returns:
            Valeur nettoyée
        """
        if pd.isna(value):
            return value
        
        if column_type == 'text':
            return self._normalize_text(str(value))
        elif column_type == 'price':
            try:
                return round(float(value), 2)
            except (ValueError, TypeError):
                return np.nan
        elif column_type == 'status':
            status_str = str(value).strip().upper()
            return np.nan if status_str == 'NAN' else status_str
        
        return value
