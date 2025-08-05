#!/usr/bin/env python3
"""
Simple Lookup Processor - Lookup en lecture seule
Enrichit les données d'entrée avec les informations du Master BOM sans le modifier
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

class SimpleLookupProcessor:
    """Processeur de lookup simple en lecture seule"""
    
    def __init__(self):
        self.logger = logging.getLogger("SimpleLookupProcessor")
        self.stats = {
            'total_rows': 0,
            'matched_rows': 0,
            'unmatched_rows': 0,
            'processing_time': 0
        }
    
    def perform_simple_lookup(self, input_df: pd.DataFrame, master_bom: pd.DataFrame, 
                             project_column: str, key_column: str = 'PN') -> pd.DataFrame:
        """
        Effectue un lookup simple en lecture seule
        
        Args:
            input_df: Données d'entrée
            master_bom: Master BOM (non modifié)
            project_column: Colonne de projet sélectionnée
            key_column: Colonne clé pour le lookup (défaut: PN)
            
        Returns:
            DataFrame enrichi avec les informations du Master BOM
        """
        start_time = datetime.now()
        self.logger.info("=== DÉBUT LOOKUP SIMPLE EN LECTURE SEULE ===")
        
        # Copier les données d'entrée pour ne pas les modifier
        result_df = input_df.copy()
        self.stats['total_rows'] = len(result_df)
        
        # Vérifier les colonnes requises
        if key_column not in result_df.columns:
            raise ValueError(f"Colonne clé '{key_column}' non trouvée dans les données d'entrée")
        
        if 'Project' not in result_df.columns:
            raise ValueError("Colonne 'Project' non trouvée dans les données d'entrée")
        
        # Déterminer la colonne PN dans le Master BOM
        master_pn_col = self._find_master_pn_column(master_bom)
        self.logger.info(f"Colonne PN du Master BOM: {master_pn_col}")
        
        # Déterminer la colonne de projet dans le Master BOM
        master_project_col = self._find_master_project_column(master_bom, project_column)
        self.logger.info(f"Colonne projet du Master BOM: {master_project_col}")
        
        # Créer les clés de lookup composites (PN + Project)
        self.logger.info("Création des clés de lookup...")
        
        # Clé pour les données d'entrée
        input_lookup_key = (result_df[key_column].astype(str) + '|' + 
                           result_df['Project'].astype(str))
        
        # Clé pour le Master BOM
        master_lookup_key = (master_bom[master_pn_col].astype(str) + '|' + 
                            master_bom[master_project_col].astype(str))
        
        # Préparer le Master BOM pour le lookup
        master_for_lookup = master_bom.copy()
        master_for_lookup['lookup_key'] = master_lookup_key
        
        # Supprimer les doublons (garder le premier comme VLOOKUP)
        master_unique = master_for_lookup.drop_duplicates(subset=['lookup_key'], keep='first')
        
        self.logger.info(f"Master BOM: {len(master_unique)} entrées uniques pour le lookup")
        
        # Effectuer le lookup pour chaque colonne d'intérêt
        columns_to_lookup = ['Status', 'Description', 'Price', 'Supplier']
        
        for col in columns_to_lookup:
            if col in master_unique.columns:
                self.logger.info(f"Lookup de la colonne: {col}")
                
                # Créer le dictionnaire de lookup
                lookup_series = master_unique[col].fillna("" if col != 'Status' else "Unknown")
                lookup_dict = pd.Series(lookup_series.values, 
                                      index=master_unique['lookup_key']).to_dict()
                
                # Effectuer le mapping
                mapped_values = input_lookup_key.map(lookup_dict)
                
                # Ajouter la colonne au résultat
                if col in result_df.columns:
                    result_df[f'{col}_Master'] = mapped_values
                else:
                    result_df[col] = mapped_values
        
        # Ajouter des colonnes d'information
        result_df['Lookup_Key'] = input_lookup_key
        result_df['Lookup_Status'] = input_lookup_key.map(
            pd.Series(['Found'] * len(master_unique), index=master_unique['lookup_key'])
        ).fillna('Not_Found')
        
        # Calculer les statistiques
        self.stats['matched_rows'] = (result_df['Lookup_Status'] == 'Found').sum()
        self.stats['unmatched_rows'] = (result_df['Lookup_Status'] == 'Not_Found').sum()
        
        # Ajouter des colonnes de traitement simples
        result_df['Processing_Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_df['Notes'] = result_df['Lookup_Status'].map({
            'Found': 'Informations trouvées dans Master BOM',
            'Not_Found': 'PN non trouvé dans Master BOM pour ce projet'
        })
        
        # Calculer le temps de traitement
        end_time = datetime.now()
        self.stats['processing_time'] = (end_time - start_time).total_seconds()
        
        self._log_summary()
        
        self.logger.info("=== LOOKUP SIMPLE TERMINÉ ===")
        return result_df
    
    def _find_master_pn_column(self, master_bom: pd.DataFrame) -> str:
        """Trouve la colonne PN dans le Master BOM"""
        possible_pn_columns = ['PN', 'Yazaki PN', 'YAZAKI PN', 'yazaki pn', 'Part Number']
        
        for col in possible_pn_columns:
            if col in master_bom.columns:
                return col
        
        # Si aucune colonne standard trouvée, prendre la première qui contient 'PN'
        for col in master_bom.columns:
            if 'PN' in col.upper():
                return col
        
        raise ValueError("Aucune colonne PN trouvée dans le Master BOM")
    
    def _find_master_project_column(self, master_bom: pd.DataFrame, project_column: str) -> str:
        """Trouve la colonne de projet dans le Master BOM"""
        # D'abord essayer la colonne exacte
        if project_column in master_bom.columns:
            return project_column
        
        # Chercher des colonnes similaires
        for col in master_bom.columns:
            if project_column.lower() in col.lower() or col.lower() in project_column.lower():
                return col
        
        # Fallback vers des colonnes génériques
        generic_project_columns = ['Project', 'PROJECT', 'project']
        for col in generic_project_columns:
            if col in master_bom.columns:
                self.logger.warning(f"Colonne '{project_column}' non trouvée, utilisation de '{col}'")
                return col
        
        raise ValueError(f"Colonne de projet '{project_column}' non trouvée dans le Master BOM")
    
    def _log_summary(self):
        """Log le résumé du traitement"""
        self.logger.info("=== RÉSUMÉ DU LOOKUP SIMPLE ===")
        self.logger.info(f"Total des lignes: {self.stats['total_rows']}")
        self.logger.info(f"Correspondances trouvées: {self.stats['matched_rows']}")
        self.logger.info(f"Non trouvées: {self.stats['unmatched_rows']}")
        self.logger.info(f"Taux de correspondance: {self.stats['matched_rows']/self.stats['total_rows']*100:.1f}%")
        self.logger.info(f"Temps de traitement: {self.stats['processing_time']:.2f}s")
        self.logger.info("=" * 35)
    
    def get_stats(self) -> dict:
        """Retourne les statistiques du traitement"""
        return self.stats.copy()
    
    def save_result(self, result_df: pd.DataFrame, output_path: str) -> bool:
        """
        Sauvegarde le résultat dans un fichier Excel
        
        Args:
            result_df: DataFrame résultat
            output_path: Chemin de sortie
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Créer le répertoire si nécessaire
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder avec formatage
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                result_df.to_excel(writer, sheet_name='Enriched_Data', index=False)
                
                # Ajouter une feuille de statistiques
                stats_df = pd.DataFrame([self.stats])
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            self.logger.info(f"Résultat sauvegardé: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False

def test_simple_lookup():
    """Test du lookup simple"""
    print("🧪 TEST DU LOOKUP SIMPLE")
    print("=" * 40)
    
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    try:
        # Charger les données
        master_bom_path = Path("Master_BOM_Real.xlsx")
        if not master_bom_path.exists():
            print("❌ Master BOM non trouvé")
            return False
        
        input_file = Path("Sample_Input_Data.xlsx")
        if not input_file.exists():
            print("❌ Fichier d'entrée non trouvé")
            return False
        
        print("📁 Chargement des données...")
        master_bom = pd.read_excel(master_bom_path)
        input_df = pd.read_excel(input_file)
        
        print(f"   Master BOM: {len(master_bom)} lignes")
        print(f"   Données d'entrée: {len(input_df)} lignes")
        
        # Effectuer le lookup
        processor = SimpleLookupProcessor()
        result_df = processor.perform_simple_lookup(
            input_df, master_bom, 'V710_AWD_PP_YOTK', 'PN'
        )
        
        # Sauvegarder le résultat
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/Simple_Lookup_Result_{timestamp}.xlsx"
        
        success = processor.save_result(result_df, output_path)
        
        if success:
            print(f"✅ Résultat sauvegardé: {output_path}")
            stats = processor.get_stats()
            print(f"📊 Statistiques:")
            print(f"   - Total: {stats['total_rows']} lignes")
            print(f"   - Trouvées: {stats['matched_rows']} ({stats['matched_rows']/stats['total_rows']*100:.1f}%)")
            print(f"   - Non trouvées: {stats['unmatched_rows']}")
            return True
        else:
            print("❌ Erreur lors de la sauvegarde")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_simple_lookup()
