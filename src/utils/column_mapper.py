#!/usr/bin/env python3
"""
Utilitaire pour mapper les noms de colonnes avec des variantes
"""

import re
from typing import Dict, List, Optional

class ColumnMapper:
    """Classe pour mapper les noms de colonnes avec des variantes."""
    
    def __init__(self):
        """Initialise le mapper avec les correspondances de colonnes."""
        self.column_mappings = {
            'PN': [
                'PN',
                'Part Number',
                'Part_Number',
                'PartNumber',
                'Yazaki Part Number',
                'YAZAKI PART NUMBER',
                'yazaki part number',
                'YAZAKI PN',
                'yazaki pn',
                'Yazaki PN',
                'P/N',
                'Part No',
                'Part_No',
                'PartNo',
                'Component',
                'Component_Number',
                'Reference'
            ],
            'Project': [
                'Project',
                'PROJECT',
                'project',
                'BOM As Filter',
                'BOM_As_Filter',
                'BOMAsFilter',
                'bom as filter',
                'BOM AS FILTER',
                'BOM ASL FILTER',
                'bom asl filter',
                'Bom Asl Filter',
                'Filter',
                'Project_Name',
                'ProjectName',
                'Project Name',
                'Application',
                'Program',
                'Model'
            ],
            'Price': [
                'Price',
                'PRICE',
                'price',
                'Cost',
                'Unit_Price',
                'Unit Price',
                'UnitPrice',
                'Amount',
                'Value'
            ],
            'Supplier': [
                'Supplier',
                'SUPPLIER',
                'supplier',
                'Vendor',
                'Manufacturer',
                'Source',
                'Provider'
            ],
            'Description': [
                'Description',
                'DESCRIPTION',
                'description',
                'Desc',
                'Component_Description',
                'Component Description',
                'Part_Description',
                'Part Description',
                'Details',
                'Name'
            ],
            'Status': [
                'Status',
                'STATUS',
                'status',
                'State',
                'Condition',
                'Phase'
            ]
        }
    
    def normalize_column_name(self, column_name: str) -> str:
        """Normalise un nom de colonne en supprimant espaces et caractères spéciaux."""
        if not column_name:
            return ""
        
        # Supprimer les espaces en début/fin
        normalized = str(column_name).strip()
        
        # Remplacer les caractères spéciaux par des espaces
        normalized = re.sub(r'[_\-\.\(\)\[\]]', ' ', normalized)
        
        # Supprimer les espaces multiples
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def find_column_match(self, target_column: str, available_columns: List[str]) -> Optional[str]:
        """
        Trouve la meilleure correspondance pour une colonne cible.
        
        Args:
            target_column: Nom de la colonne recherchée (ex: 'PN', 'Project')
            available_columns: Liste des colonnes disponibles dans le fichier
            
        Returns:
            Nom de la colonne correspondante ou None si non trouvée
        """
        if target_column not in self.column_mappings:
            return None
        
        possible_names = self.column_mappings[target_column]
        
        # Recherche exacte d'abord
        for available_col in available_columns:
            if available_col in possible_names:
                return available_col
        
        # Recherche insensible à la casse
        for available_col in available_columns:
            for possible_name in possible_names:
                if available_col.lower() == possible_name.lower():
                    return available_col
        
        # Recherche avec normalisation
        for available_col in available_columns:
            normalized_available = self.normalize_column_name(available_col)
            
            for possible_name in possible_names:
                normalized_possible = self.normalize_column_name(possible_name)
                
                if normalized_available.lower() == normalized_possible.lower():
                    return available_col
        
        # Recherche partielle (contient)
        for available_col in available_columns:
            normalized_available = self.normalize_column_name(available_col).lower()
            
            for possible_name in possible_names:
                normalized_possible = self.normalize_column_name(possible_name).lower()
                
                if (normalized_possible in normalized_available or 
                    normalized_available in normalized_possible):
                    return available_col
        
        return None
    
    def map_columns(self, available_columns: List[str]) -> Dict[str, Optional[str]]:
        """
        Mappe toutes les colonnes requises avec les colonnes disponibles.
        
        Args:
            available_columns: Liste des colonnes disponibles dans le fichier
            
        Returns:
            Dictionnaire {colonne_standard: colonne_fichier}
        """
        mapping = {}
        
        for target_column in self.column_mappings.keys():
            matched_column = self.find_column_match(target_column, available_columns)
            mapping[target_column] = matched_column
        
        return mapping
    
    def get_required_columns_mapping(self, available_columns: List[str]) -> Dict[str, str]:
        """
        Retourne le mapping pour les colonnes obligatoires uniquement.
        
        Args:
            available_columns: Liste des colonnes disponibles
            
        Returns:
            Dictionnaire des colonnes obligatoires mappées
        """
        required_columns = ['PN', 'Project']
        mapping = {}
        
        for col in required_columns:
            matched = self.find_column_match(col, available_columns)
            if matched:
                mapping[col] = matched
        
        return mapping
    
    def validate_required_columns(self, available_columns: List[str]) -> tuple[bool, List[str]]:
        """
        Valide que toutes les colonnes obligatoires sont présentes.
        
        Args:
            available_columns: Liste des colonnes disponibles
            
        Returns:
            (is_valid, missing_columns)
        """
        required_columns = ['PN', 'Project']
        missing_columns = []
        
        for col in required_columns:
            matched = self.find_column_match(col, available_columns)
            if not matched:
                missing_columns.append(col)
        
        return len(missing_columns) == 0, missing_columns
    
    def get_mapping_info(self, available_columns: List[str]) -> Dict:
        """
        Retourne des informations détaillées sur le mapping.
        
        Args:
            available_columns: Liste des colonnes disponibles
            
        Returns:
            Dictionnaire avec les informations de mapping
        """
        mapping = self.map_columns(available_columns)
        is_valid, missing = self.validate_required_columns(available_columns)
        
        return {
            'mapping': mapping,
            'is_valid': is_valid,
            'missing_required': missing,
            'available_columns': available_columns,
            'mapped_columns': {k: v for k, v in mapping.items() if v is not None}
        }
