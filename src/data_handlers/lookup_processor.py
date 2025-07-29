"""
Processeur de lookup pour le Component Data Processor.

Gère la logique de recherche et de traitement des données
basée sur les statuts des composants dans le Master BOM.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

from ..utils.logger import Logger


class LookupProcessor:
    """Processeur pour les opérations de lookup et traitement des statuts."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialise le processeur de lookup.
        
        Args:
            logger: Instance de logger (optionnel)
        """
        self.logger = logger or Logger("LookupProcessor")
        
        # Statistiques de traitement
        self.processing_stats = {
            'total_processed': 0,
            'status_d_updates': 0,
            'status_0_duplicates': 0,
            'status_nan_unknowns': 0,
            'status_x_skipped': 0,
            'lookup_matches': 0,
            'lookup_misses': 0
        }
        
        # Lignes additionnelles créées
        self.additional_rows = []
    
    def perform_lookup(self, input_df: pd.DataFrame, master_bom: pd.DataFrame) -> pd.DataFrame:
        """
        Effectue le lookup entre les données d'entrée et le Master BOM.
        
        Args:
            input_df: DataFrame des données d'entrée nettoyées
            master_bom: DataFrame du Master BOM
            
        Returns:
            DataFrame avec les résultats du lookup
        """
        self.logger.info("Début du processus de lookup")
        
        # Réinitialiser les statistiques
        self._reset_stats()
        
        # Créer les clés de lookup
        input_df = self._create_lookup_keys(input_df)
        master_bom = self._create_lookup_keys(master_bom)
        
        # Effectuer le merge
        lookup_result = self._perform_merge(input_df, master_bom)
        
        # Ajouter les colonnes de traitement
        lookup_result = self._add_processing_columns(lookup_result)
        
        self.logger.info(f"Lookup terminé: {len(lookup_result)} lignes traitées")
        
        return lookup_result
    
    def process_lookup_results(self, df: pd.DataFrame, master_bom: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Traite les résultats du lookup selon la logique métier.

        Args:
            df: DataFrame avec les résultats du lookup
            master_bom: DataFrame du Master BOM (pour les mises à jour)

        Returns:
            Tuple (DataFrame traité, Master BOM mis à jour)
        """
        self.logger.info("Début du traitement des résultats de lookup")

        # Réinitialiser les lignes additionnelles
        self.additional_rows = []

        # S'assurer que le master_bom a les clés de lookup
        if 'lookup_key' not in master_bom.columns:
            master_bom = self._create_lookup_keys(master_bom)

        # Traiter chaque ligne selon son statut
        for idx, row in df.iterrows():
            self._process_single_row(idx, row, df, master_bom)
        
        # Ajouter les lignes additionnelles
        if self.additional_rows:
            additional_df = pd.DataFrame(self.additional_rows)
            df = pd.concat([df, additional_df], ignore_index=True)
            self.logger.info(f"Ajout de {len(self.additional_rows)} lignes additionnelles")
        
        self._log_processing_summary()
        
        return df, master_bom
    
    def _reset_stats(self):
        """Réinitialise les statistiques de traitement."""
        for key in self.processing_stats:
            self.processing_stats[key] = 0
        self.additional_rows = []
    
    def _create_lookup_keys(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée les clés de lookup en combinant PN et Project.
        
        Args:
            df: DataFrame source
            
        Returns:
            DataFrame avec la colonne lookup_key ajoutée
        """
        df = df.copy()
        df['lookup_key'] = (
            df['PN'].astype(str).str.strip() + '_' + 
            df['Project'].astype(str).str.strip()
        )
        return df
    
    def _perform_merge(self, input_df: pd.DataFrame, master_bom: pd.DataFrame) -> pd.DataFrame:
        """
        Effectue le merge entre input et master BOM.
        
        Args:
            input_df: DataFrame d'entrée
            master_bom: DataFrame Master BOM
            
        Returns:
            DataFrame mergé
        """
        # Sélectionner les colonnes nécessaires du Master BOM
        master_cols = ['lookup_key', 'Status']
        if 'Description' in master_bom.columns:
            master_cols.append('Description')
        
        master_subset = master_bom[master_cols].copy()
        
        # Effectuer le merge
        result = input_df.merge(
            master_subset,
            on='lookup_key',
            how='left',
            suffixes=('', '_master')
        )
        
        # Compter les matches et misses
        self.processing_stats['lookup_matches'] = result['Status'].notna().sum()
        self.processing_stats['lookup_misses'] = result['Status'].isna().sum()
        
        self.logger.info(f"Lookup: {self.processing_stats['lookup_matches']} matches, "
                        f"{self.processing_stats['lookup_misses']} misses")
        
        return result
    
    def _add_processing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajoute les colonnes nécessaires pour le traitement."""
        df['Notes'] = ''
        df['Action'] = ''
        return df
    
    def _process_single_row(self, idx: int, row: pd.Series, df: pd.DataFrame, master_bom: pd.DataFrame):
        """
        Traite une ligne individuelle selon son statut.
        
        Args:
            idx: Index de la ligne
            row: Série pandas de la ligne
            df: DataFrame principal
            master_bom: Master BOM pour les mises à jour
        """
        status = row.get('Status', np.nan)
        self.processing_stats['total_processed'] += 1
        
        if pd.isna(status):
            # Cas 3: Status = NaN - Composant inconnu
            self._handle_status_nan(row)
            
        elif str(status).upper() == 'D':
            # Cas 1: Status = D - Composant déprécié
            self._handle_status_d(idx, row, df, master_bom)
            
        elif str(status) == '0':
            # Cas 2: Status = 0 - Doublon ou correspondance incertaine
            self._handle_status_0(row)
            
        elif str(status).upper() == 'X':
            # Cas 4: Status = X - Déjà marqué comme ancien
            self._handle_status_x(idx, row, df)
        
        else:
            # Statut non reconnu ou actif
            self._handle_other_status(idx, row, df, status)
    
    def _handle_status_d(self, idx: int, row: pd.Series, df: pd.DataFrame, master_bom: pd.DataFrame):
        """Gère le cas Status = 'D' (Déprécié)."""
        # Mettre à jour le Master BOM
        lookup_key = row['lookup_key']
        mask = master_bom['lookup_key'] == lookup_key
        
        if mask.any():
            master_bom.loc[mask, 'Status'] = 'X'
            
            # Ajouter un commentaire à la ligne actuelle
            df.at[idx, 'Notes'] = 'Status D mis à jour vers X'
            df.at[idx, 'Action'] = 'Updated'
            
            self.processing_stats['status_d_updates'] += 1
            self.logger.debug(f"Mise à jour D→X: PN={row['PN']}, Project={row['Project']}")
    
    def _handle_status_0(self, row: pd.Series):
        """Gère le cas Status = '0' (Doublon)."""
        new_row = {
            'PN': row['PN'],
            'Project': row['Project'],
            'Price': '',
            'Description': '',
            'Supplier': '',
            'Notes': 'Doublon ou correspondance incertaine - vérification manuelle nécessaire',
            'Action': 'Duplicate_Added',
            'Status': '0',
            'lookup_key': row['lookup_key']
        }
        
        self.additional_rows.append(new_row)
        self.processing_stats['status_0_duplicates'] += 1
        self.logger.debug(f"Ajout doublon: PN={row['PN']}, Project={row['Project']}")
    
    def _handle_status_nan(self, row: pd.Series):
        """Gère le cas Status = NaN (Inconnu)."""
        new_row = {
            'PN': row['PN'],
            'Project': row['Project'],
            'Price': '',
            'Description': '',
            'Supplier': '',
            'Notes': 'PN inconnu – entrée potentiellement nouvelle',
            'Action': 'Unknown_Added',
            'Status': np.nan,
            'lookup_key': row['lookup_key']
        }
        
        self.additional_rows.append(new_row)
        self.processing_stats['status_nan_unknowns'] += 1
        self.logger.debug(f"Ajout inconnu: PN={row['PN']}, Project={row['Project']}")
    
    def _handle_status_x(self, idx: int, row: pd.Series, df: pd.DataFrame):
        """Gère le cas Status = 'X' (Déjà ancien)."""
        df.at[idx, 'Notes'] = 'Composant déjà marqué comme ancien - ignoré'
        df.at[idx, 'Action'] = 'Skipped'
        
        self.processing_stats['status_x_skipped'] += 1
        self.logger.debug(f"Ignoré (status X): PN={row['PN']}, Project={row['Project']}")
    
    def _handle_other_status(self, idx: int, row: pd.Series, df: pd.DataFrame, status: Any):
        """Gère les autres statuts (actifs ou non reconnus)."""
        if str(status).upper() == 'A':
            df.at[idx, 'Notes'] = 'Composant actif - aucune action requise'
            df.at[idx, 'Action'] = 'No_Action'
        else:
            df.at[idx, 'Notes'] = f'Statut non reconnu: {status}'
            df.at[idx, 'Action'] = 'Unknown_Status'
        
        self.logger.debug(f"Autre statut ({status}): PN={row['PN']}, Project={row['Project']}")
    
    def _log_processing_summary(self):
        """Log un résumé du traitement."""
        self.logger.info("=== RÉSUMÉ DU TRAITEMENT ===")
        for key, value in self.processing_stats.items():
            self.logger.info(f"{key.replace('_', ' ').title()}: {value}")
        self.logger.info("=" * 32)
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de traitement.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        return self.processing_stats.copy()
    
    def validate_master_bom(self, master_bom: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valide la structure du Master BOM.
        
        Args:
            master_bom: DataFrame du Master BOM
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Vérifier les colonnes requises
        required_cols = ['PN', 'Project', 'Status']
        missing_cols = set(required_cols) - set(master_bom.columns)
        
        if missing_cols:
            errors.append(f"Colonnes manquantes dans Master BOM: {list(missing_cols)}")
        
        # Vérifier qu'il n'est pas vide
        if master_bom.empty:
            errors.append("Master BOM vide")
        
        # Vérifier les doublons de clés
        if 'PN' in master_bom.columns and 'Project' in master_bom.columns:
            master_bom_temp = master_bom.copy()
            master_bom_temp['lookup_key'] = (
                master_bom_temp['PN'].astype(str) + '_' + 
                master_bom_temp['Project'].astype(str)
            )
            
            duplicates = master_bom_temp['lookup_key'].duplicated().sum()
            if duplicates > 0:
                errors.append(f"Doublons détectés dans Master BOM: {duplicates}")
        
        return len(errors) == 0, errors
    
    def create_lookup_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Crée un résumé détaillé du lookup.
        
        Args:
            df: DataFrame traité
            
        Returns:
            Dictionnaire avec le résumé
        """
        summary = self.get_processing_statistics()
        
        # Ajouter des statistiques supplémentaires
        if 'Action' in df.columns:
            action_counts = df['Action'].value_counts().to_dict()
            summary.update({f'action_{k}': v for k, v in action_counts.items()})
        
        # Calculer les pourcentages
        total = summary.get('total_processed', 0)
        if total > 0:
            summary['match_rate'] = round((summary['lookup_matches'] / total) * 100, 2)
            summary['miss_rate'] = round((summary['lookup_misses'] / total) * 100, 2)
        
        return summary
