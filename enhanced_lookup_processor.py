#!/usr/bin/env python3
"""
Enhanced Lookup Processor - Inspiré du projet ETL-Automated-Tool
Logique de lookup avancée avec suggestion de colonnes intelligente
"""

import pandas as pd
from difflib import SequenceMatcher
from typing import Tuple, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class EnhancedLookupProcessor:
    """Processeur de lookup avancé avec logique inspirée d'ETL-Automated-Tool"""
    
    @staticmethod
    def suggest_column(input_name: str, columns: List[str]) -> Tuple[str, float]:
        """
        Suggère la meilleure colonne correspondante avec score de confiance
        
        Args:
            input_name: Nom d'entrée à matcher (ex: "J74_V710_B2_PP_YOTK")
            columns: Liste des colonnes disponibles
            
        Returns:
            (suggested_column, confidence_score)
        """
        if not input_name.strip():
            return columns[0] if columns else "", 0.0
        
        # Extraire préfixe et suffixe (ex: J74_V710_B2_PP_YOTK -> J74_V710_B2, YOTK)
        parts = input_name.split('_')
        if len(parts) >= 4:
            prefix = '_'.join(parts[:3])  # 3 premières parties
            suffix = parts[-1]  # Dernière partie
            
            best, best_score = input_name, 0
            
            # Recherche par préfixe et suffixe
            for col in columns:
                if (col.upper().startswith(prefix.upper()) and 
                    col.upper().endswith(suffix.upper())):
                    score = SequenceMatcher(None, input_name.lower(), col.lower()).ratio()
                    if score >= 0.9 and score > best_score:  # Seuil 90%
                        best, best_score = col, score
            
            if best_score > 0:
                return best, best_score
        
        # Fallback: recherche par similarité générale
        best, best_score = input_name, 0
        for col in columns:
            score = SequenceMatcher(None, input_name.lower(), col.lower()).ratio()
            if score > best_score:
                best, best_score = col, score
        
        return best, best_score
    
    @staticmethod
    def add_activation_status(
        master_df: pd.DataFrame,
        target_df: pd.DataFrame,
        key_col: str,
        lookup_col: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Ajoute le statut d'activation avec statistiques détaillées

        Args:
            master_df: DataFrame master (Master BOM)
            target_df: DataFrame cible (fichier d'entrée)
            key_col: Colonne clé pour le lookup (ex: "PN")
            lookup_col: Colonne de lookup (ex: "V710_B2_J74_JOB1+90_YMOK")

        Returns:
            (result_dataframe, lookup_stats)
        """
        # Trouver la colonne PN dans le Master BOM
        master_pn_col = None
        possible_pn_cols = ['PN', 'Yazaki PN', 'YAZAKI PN', 'yazaki pn', 'Part Number']

        for col in possible_pn_cols:
            if col in master_df.columns:
                master_pn_col = col
                break

        if master_pn_col is None:
            # Chercher une colonne contenant 'PN'
            for col in master_df.columns:
                if 'PN' in col.upper():
                    master_pn_col = col
                    break

        if master_pn_col is None:
            raise ValueError(f"Aucune colonne PN trouvée dans le Master BOM. Colonnes disponibles: {list(master_df.columns)}")

        logger.info(f"Colonne PN du Master BOM: {master_pn_col}")

        # Supprimer les doublons du master
        master_clean = master_df.drop_duplicates(subset=[master_pn_col], keep='first')
        
        # Vérifier que la colonne de lookup existe
        if lookup_col not in master_clean.columns:
            raise ValueError(f"Colonne de lookup '{lookup_col}' non trouvée dans le Master BOM. Colonnes disponibles: {list(master_clean.columns)}")

        logger.info(f"Colonne de lookup: {lookup_col}")

        # Préparer le dictionnaire de lookup
        lookup_series = master_clean[lookup_col]
        lookup_dict = pd.Series(
            lookup_series.values,
            index=master_clean[master_pn_col]
        ).to_dict()
        
        # Statistiques initiales
        stats = {
            "master_records": len(master_df),
            "master_unique_records": len(master_clean),
            "target_records": len(target_df),
            "lookup_dict_size": len(lookup_dict),
            "mapping_results": {}
        }
        
        df = target_df.copy()
        
        def get_status(key):
            """Logique de mapping inspirée d'ETL-Automated-Tool"""
            if pd.isna(key):
                return "MISSING_KEY"  # Clé manquante/null dans target
            elif key in lookup_dict:
                val = lookup_dict[key]
                return val if pd.notna(val) else "0"  # Clé trouvée, valeur null -> "0"
            else:
                return "NOT_FOUND"  # Clé non trouvée dans master
        
        # Appliquer la logique de mapping
        df.insert(1, 'ACTIVATION_STATUS', df[key_col].apply(get_status))
        
        # Calculer les statistiques de mapping
        status_counts = df['ACTIVATION_STATUS'].value_counts().to_dict()
        stats["mapping_results"] = status_counts
        stats["total_processed"] = len(df)
        
        # Calculer les pourcentages
        total = len(df)
        stats["mapping_percentages"] = {
            status: round((count / total) * 100, 2)
            for status, count in status_counts.items()
        }
        
        logger.info(f"Lookup completed: {stats}")
        return df, stats
    
    @staticmethod
    def get_column_suggestions(
        master_df: pd.DataFrame, 
        start_col: int = 1, 
        end_col: int = 22
    ) -> List[str]:
        """
        Obtient les colonnes permises pour le lookup depuis le master dataframe
        
        Args:
            master_df: DataFrame master
            start_col: Index de début (défaut: 1)
            end_col: Index de fin (défaut: 22)
            
        Returns:
            Liste des colonnes suggérées
        """
        columns = list(master_df.columns)
        # Retourner les colonnes dans la plage spécifiée
        end_idx = min(end_col, len(columns))
        return columns[start_col:end_idx]
    
    @staticmethod
    def analyze_project_columns(master_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse les colonnes de projets avec statistiques de remplissage
        
        Args:
            master_df: DataFrame master
            
        Returns:
            Dictionnaire avec analyse des colonnes
        """
        columns = EnhancedLookupProcessor.get_column_suggestions(master_df)
        analysis = {
            "total_columns": len(columns),
            "columns_analysis": []
        }
        
        for col in columns:
            if col in master_df.columns:
                non_null_count = master_df[col].notna().sum()
                total_count = len(master_df)
                fill_percentage = round((non_null_count / total_count) * 100, 1)
                
                analysis["columns_analysis"].append({
                    "name": col,
                    "fill_count": int(non_null_count),
                    "total_count": int(total_count),
                    "fill_percentage": fill_percentage,
                    "is_project_column": "V710" in col.upper() or "J74" in col.upper()
                })
        
        # Trier par pourcentage de remplissage décroissant
        analysis["columns_analysis"].sort(
            key=lambda x: x["fill_percentage"], 
            reverse=True
        )
        
        return analysis
    
    @staticmethod
    def find_best_project_column(
        master_df: pd.DataFrame, 
        project_hint: str = ""
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Trouve la meilleure colonne de projet basée sur un indice
        
        Args:
            master_df: DataFrame master
            project_hint: Indice de projet (ex: "FORD_J74_V710_B2_PP_YOTK")
            
        Returns:
            (best_column, confidence, analysis)
        """
        analysis = EnhancedLookupProcessor.analyze_project_columns(master_df)
        columns = [col["name"] for col in analysis["columns_analysis"]]
        
        if project_hint:
            best_col, confidence = EnhancedLookupProcessor.suggest_column(
                project_hint, columns
            )
        else:
            # Prendre la colonne avec le meilleur remplissage
            if analysis["columns_analysis"]:
                best_col = analysis["columns_analysis"][0]["name"]
                confidence = analysis["columns_analysis"][0]["fill_percentage"] / 100
            else:
                best_col, confidence = "", 0.0
        
        return best_col, confidence, analysis

# Instance globale du processeur
enhanced_lookup_processor = EnhancedLookupProcessor()
