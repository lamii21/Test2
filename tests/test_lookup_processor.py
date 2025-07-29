"""
Tests unitaires pour le module LookupProcessor.
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_handlers.lookup_processor import LookupProcessor
from src.utils.logger import Logger


class TestLookupProcessor(unittest.TestCase):
    """Tests pour la classe LookupProcessor."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.logger = Mock(spec=Logger)
        self.processor = LookupProcessor(self.logger)
        
        # Données de test pour Master BOM
        self.master_bom_data = {
            'PN': ['RES001', 'CAP002', 'IC003', 'LED004', 'OLD006'],
            'Project': ['PROJ_A', 'PROJ_B', 'PROJ_A', 'PROJ_C', 'PROJ_D'],
            'Status': ['D', '0', 'A', 'X', 'A'],
            'Description': ['Resistor', 'Capacitor', 'IC', 'LED', 'Old Component']
        }
        self.master_bom = pd.DataFrame(self.master_bom_data)
        
        # Données de test pour input
        self.input_data = {
            'PN': ['RES001', 'CAP002', 'NEW001', 'LED004', 'IC003'],
            'Project': ['PROJ_A', 'PROJ_B', 'PROJ_NEW', 'PROJ_C', 'PROJ_A'],
            'Price': [0.05, 0.15, 1.50, 0.08, 2.50],
            'Supplier': ['SUP1', 'SUP2', 'SUP3', 'SUP1', 'SUP3']
        }
        self.input_df = pd.DataFrame(self.input_data)
    
    def test_create_lookup_keys(self):
        """Test la création des clés de lookup."""
        df_with_keys = self.processor._create_lookup_keys(self.input_df)
        
        self.assertIn('lookup_key', df_with_keys.columns)
        self.assertEqual(df_with_keys.iloc[0]['lookup_key'], 'RES001_PROJ_A')
        self.assertEqual(df_with_keys.iloc[1]['lookup_key'], 'CAP002_PROJ_B')
    
    def test_perform_lookup(self):
        """Test le processus de lookup."""
        result_df = self.processor.perform_lookup(self.input_df, self.master_bom)
        
        # Vérifier que les colonnes nécessaires sont présentes
        self.assertIn('Status', result_df.columns)
        self.assertIn('Notes', result_df.columns)
        self.assertIn('Action', result_df.columns)
        self.assertIn('lookup_key', result_df.columns)
        
        # Vérifier les matches
        self.assertEqual(result_df.iloc[0]['Status'], 'D')  # RES001_PROJ_A
        self.assertEqual(result_df.iloc[1]['Status'], '0')  # CAP002_PROJ_B
        self.assertTrue(pd.isna(result_df.iloc[2]['Status']))  # NEW001_PROJ_NEW (pas dans master)
    
    def test_process_status_d(self):
        """Test le traitement du statut D (déprécié)."""
        # Préparer les données
        lookup_df = self.processor.perform_lookup(self.input_df, self.master_bom)
        master_bom_copy = self.master_bom.copy()
        
        # Traiter les résultats
        processed_df, updated_master_bom = self.processor.process_lookup_results(
            lookup_df, master_bom_copy
        )
        
        # Vérifier que le statut D a été mis à jour vers X dans le Master BOM
        res001_mask = (updated_master_bom['PN'] == 'RES001') & (updated_master_bom['Project'] == 'PROJ_A')
        self.assertEqual(updated_master_bom.loc[res001_mask, 'Status'].iloc[0], 'X')
        
        # Vérifier les statistiques
        stats = self.processor.get_processing_statistics()
        self.assertGreater(stats['status_d_updates'], 0)
    
    def test_process_status_0(self):
        """Test le traitement du statut 0 (doublon)."""
        lookup_df = self.processor.perform_lookup(self.input_df, self.master_bom)
        
        processed_df, _ = self.processor.process_lookup_results(lookup_df, self.master_bom)
        
        # Vérifier qu'une ligne supplémentaire a été ajoutée pour le doublon
        duplicate_rows = processed_df[processed_df['Action'] == 'Duplicate_Added']
        self.assertGreater(len(duplicate_rows), 0)
        
        # Vérifier le contenu de la ligne dupliquée
        duplicate_row = duplicate_rows.iloc[0]
        self.assertEqual(duplicate_row['PN'], 'CAP002')
        self.assertEqual(duplicate_row['Project'], 'PROJ_B')
        self.assertIn('Doublon', duplicate_row['Notes'])
    
    def test_process_status_nan(self):
        """Test le traitement du statut NaN (inconnu)."""
        lookup_df = self.processor.perform_lookup(self.input_df, self.master_bom)
        
        processed_df, _ = self.processor.process_lookup_results(lookup_df, self.master_bom)
        
        # Vérifier qu'une ligne supplémentaire a été ajoutée pour l'inconnu
        unknown_rows = processed_df[processed_df['Action'] == 'Unknown_Added']
        self.assertGreater(len(unknown_rows), 0)
        
        # Vérifier le contenu de la ligne inconnue
        unknown_row = unknown_rows.iloc[0]
        self.assertEqual(unknown_row['PN'], 'NEW001')
        self.assertEqual(unknown_row['Project'], 'PROJ_NEW')
        self.assertIn('inconnu', unknown_row['Notes'])
    
    def test_process_status_x(self):
        """Test le traitement du statut X (déjà ancien)."""
        lookup_df = self.processor.perform_lookup(self.input_df, self.master_bom)
        
        processed_df, _ = self.processor.process_lookup_results(lookup_df, self.master_bom)
        
        # Vérifier que les composants avec statut X sont ignorés
        skipped_rows = processed_df[processed_df['Action'] == 'Skipped']
        
        # Vérifier les statistiques
        stats = self.processor.get_processing_statistics()
        if stats['status_x_skipped'] > 0:
            self.assertGreater(len(skipped_rows), 0)
    
    def test_validate_master_bom(self):
        """Test la validation du Master BOM."""
        # Master BOM valide
        is_valid, errors = self.processor.validate_master_bom(self.master_bom)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Master BOM invalide (colonnes manquantes)
        invalid_bom = pd.DataFrame({'Description': ['Test']})
        is_valid, errors = self.processor.validate_master_bom(invalid_bom)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Master BOM vide
        empty_bom = pd.DataFrame(columns=['PN', 'Project', 'Status'])
        is_valid, errors = self.processor.validate_master_bom(empty_bom)
        self.assertFalse(is_valid)
        self.assertIn('vide', ' '.join(errors))
    
    def test_processing_statistics(self):
        """Test les statistiques de traitement."""
        lookup_df = self.processor.perform_lookup(self.input_df, self.master_bom)
        self.processor.process_lookup_results(lookup_df, self.master_bom)
        
        stats = self.processor.get_processing_statistics()
        
        # Vérifier que toutes les clés statistiques sont présentes
        expected_keys = [
            'total_processed', 'status_d_updates', 'status_0_duplicates',
            'status_nan_unknowns', 'status_x_skipped', 'lookup_matches', 'lookup_misses'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, np.integer))
    
    def test_create_lookup_summary(self):
        """Test la création du résumé de lookup."""
        lookup_df = self.processor.perform_lookup(self.input_df, self.master_bom)
        processed_df, _ = self.processor.process_lookup_results(lookup_df, self.master_bom)
        
        summary = self.processor.create_lookup_summary(processed_df)
        
        # Vérifier que le résumé contient les informations attendues
        self.assertIn('total_processed', summary)
        self.assertIn('lookup_matches', summary)
        self.assertIn('lookup_misses', summary)
        
        # Vérifier les pourcentages si applicable
        if summary['total_processed'] > 0:
            self.assertIn('match_rate', summary)
            self.assertIn('miss_rate', summary)


class TestLookupProcessorEdgeCases(unittest.TestCase):
    """Tests pour les cas limites du LookupProcessor."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.processor = LookupProcessor()
    
    def test_empty_input(self):
        """Test avec des DataFrames vides."""
        empty_input = pd.DataFrame(columns=['PN', 'Project'])
        empty_master = pd.DataFrame(columns=['PN', 'Project', 'Status'])
        
        # Ne doit pas lever d'exception
        result = self.processor.perform_lookup(empty_input, empty_master)
        self.assertTrue(result.empty)
    
    def test_no_matches(self):
        """Test quand aucune correspondance n'est trouvée."""
        input_data = {
            'PN': ['NEW001', 'NEW002'],
            'Project': ['NEW_PROJ', 'ANOTHER_PROJ']
        }
        input_df = pd.DataFrame(input_data)
        
        master_data = {
            'PN': ['OLD001', 'OLD002'],
            'Project': ['OLD_PROJ', 'ANOTHER_OLD'],
            'Status': ['A', 'D']
        }
        master_df = pd.DataFrame(master_data)
        
        result = self.processor.perform_lookup(input_df, master_df)
        
        # Tous les statuts doivent être NaN
        self.assertTrue(result['Status'].isna().all())
        
        # Vérifier les statistiques
        stats = self.processor.get_processing_statistics()
        self.assertEqual(stats['lookup_matches'], 0)
        self.assertEqual(stats['lookup_misses'], 2)
    
    def test_duplicate_keys_in_master(self):
        """Test avec des clés dupliquées dans le Master BOM."""
        master_data = {
            'PN': ['RES001', 'RES001', 'CAP002'],
            'Project': ['PROJ_A', 'PROJ_A', 'PROJ_B'],
            'Status': ['A', 'D', 'A']
        }
        master_df = pd.DataFrame(master_data)
        
        is_valid, errors = self.processor.validate_master_bom(master_df)
        self.assertFalse(is_valid)
        self.assertTrue(any('Doublon' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
