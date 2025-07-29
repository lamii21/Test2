"""
Tests unitaires pour le module DataCleaner.
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_handlers.data_cleaner import DataCleaner
from src.utils.logger import Logger


class TestDataCleaner(unittest.TestCase):
    """Tests pour la classe DataCleaner."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.logger = Mock(spec=Logger)
        self.config = {
            'required_columns': ['PN', 'Project'],
            'text_columns': ['PN', 'Project', 'Supplier', 'Description'],
            'convert_to_uppercase': True,
            'remove_non_ascii': True,
            'trim_whitespace': True,
            'normalize_spaces': True,
            'remove_empty_rows': True
        }
        self.cleaner = DataCleaner(self.config, self.logger)
    
    def test_clean_simple_dataframe(self):
        """Test le nettoyage d'un DataFrame simple."""
        # Données d'entrée avec problèmes
        data = {
            'PN': ['  res001  ', 'cap002', '  IC003'],
            'Project': ['proj_a', '  PROJ_B  ', 'proj_c'],
            'Description': ['Resistor 10K', 'Capacitor', 'IC Micro'],
            'Price': [0.05, 0.15, 2.50]
        }
        df = pd.DataFrame(data)
        
        # Nettoyer
        cleaned_df = self.cleaner.clean_dataframe(df)
        
        # Vérifications
        self.assertEqual(len(cleaned_df), 3)
        self.assertEqual(cleaned_df.iloc[0]['PN'], 'RES001')
        self.assertEqual(cleaned_df.iloc[1]['Project'], 'PROJ_B')
        self.assertTrue(all(cleaned_df['PN'].str.isupper()))
    
    def test_remove_empty_rows(self):
        """Test la suppression des lignes vides."""
        data = {
            'PN': ['RES001', '', np.nan, 'CAP002'],
            'Project': ['PROJ_A', 'PROJ_B', '', 'PROJ_C'],
            'Description': ['Resistor', '', '', 'Capacitor']
        }
        df = pd.DataFrame(data)
        
        cleaned_df = self.cleaner.clean_dataframe(df)
        
        # Seules les lignes avec PN et Project valides doivent rester
        self.assertEqual(len(cleaned_df), 2)
        self.assertIn('RES001', cleaned_df['PN'].values)
        self.assertIn('CAP002', cleaned_df['PN'].values)
    
    def test_normalize_text(self):
        """Test la normalisation du texte."""
        # Test avec caractères spéciaux
        text_with_special = "Résistör 10K Ω"
        normalized = self.cleaner._normalize_text(text_with_special)
        
        # Doit supprimer les caractères non-ASCII
        self.assertNotIn('é', normalized)
        self.assertNotIn('ö', normalized)
        self.assertNotIn('Ω', normalized)
    
    def test_normalize_prices(self):
        """Test la normalisation des prix."""
        data = {
            'PN': ['RES001', 'CAP002'],
            'Project': ['PROJ_A', 'PROJ_B'],
            'Price': ['0.055', 2.1567]
        }
        df = pd.DataFrame(data)
        
        cleaned_df = self.cleaner.clean_dataframe(df)
        
        # Vérifier l'arrondi à 2 décimales
        self.assertEqual(cleaned_df.iloc[0]['Price'], 0.06)
        self.assertEqual(cleaned_df.iloc[1]['Price'], 2.16)
    
    def test_excluded_rows_tracking(self):
        """Test le suivi des lignes exclues."""
        data = {
            'PN': ['RES001', '', 'CAP002'],
            'Project': ['PROJ_A', 'PROJ_B', ''],
            'Description': ['Resistor', 'Missing PN', 'Missing Project']
        }
        df = pd.DataFrame(data)
        
        cleaned_df = self.cleaner.clean_dataframe(df)
        excluded_df = self.cleaner.get_excluded_rows_dataframe()
        
        # Une ligne valide, deux exclues
        self.assertEqual(len(cleaned_df), 1)
        self.assertEqual(len(excluded_df), 2)
        self.assertIn('exclusion_reason', excluded_df.columns)
    
    def test_cleaning_statistics(self):
        """Test les statistiques de nettoyage."""
        data = {
            'PN': ['  res001  ', '', 'cap002'],
            'Project': ['proj_a', 'PROJ_B', ''],
            'Description': ['Resistor', 'Missing', 'Missing Project']
        }
        df = pd.DataFrame(data)
        
        self.cleaner.clean_dataframe(df)
        stats = self.cleaner.get_cleaning_statistics()
        
        self.assertEqual(stats['original_rows'], 3)
        self.assertEqual(stats['cleaned_rows'], 1)
        self.assertEqual(stats['excluded_rows'], 2)
        self.assertGreater(stats['trimmed_values'], 0)
        self.assertGreater(stats['case_corrections'], 0)
    
    def test_clean_single_value(self):
        """Test le nettoyage d'une valeur individuelle."""
        # Test texte
        cleaned_text = self.cleaner.clean_single_value('  RES001  ', 'text')
        self.assertEqual(cleaned_text, 'RES001')
        
        # Test prix
        cleaned_price = self.cleaner.clean_single_value('2.567', 'price')
        self.assertEqual(cleaned_price, 2.57)
        
        # Test statut
        cleaned_status = self.cleaner.clean_single_value('d', 'status')
        self.assertEqual(cleaned_status, 'D')
    
    def test_validation_before_cleaning(self):
        """Test la validation avant nettoyage."""
        # DataFrame valide
        valid_data = {
            'PN': ['RES001', 'CAP002'],
            'Project': ['PROJ_A', 'PROJ_B']
        }
        valid_df = pd.DataFrame(valid_data)
        
        is_valid, errors = self.cleaner.validate_before_cleaning(valid_df)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # DataFrame invalide (colonnes manquantes)
        invalid_data = {
            'Description': ['Resistor', 'Capacitor']
        }
        invalid_df = pd.DataFrame(invalid_data)
        
        is_valid, errors = self.cleaner.validate_before_cleaning(invalid_df)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestDataCleanerEdgeCases(unittest.TestCase):
    """Tests pour les cas limites du DataCleaner."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.cleaner = DataCleaner()
    
    def test_empty_dataframe(self):
        """Test avec un DataFrame vide."""
        empty_df = pd.DataFrame()
        
        # Ne doit pas lever d'exception
        cleaned_df = self.cleaner.clean_dataframe(empty_df)
        self.assertTrue(cleaned_df.empty)
    
    def test_dataframe_with_only_nan(self):
        """Test avec un DataFrame contenant seulement des NaN."""
        data = {
            'PN': [np.nan, np.nan],
            'Project': [np.nan, np.nan],
            'Description': [np.nan, np.nan]
        }
        df = pd.DataFrame(data)
        
        cleaned_df = self.cleaner.clean_dataframe(df)
        self.assertTrue(cleaned_df.empty)
    
    def test_unicode_handling(self):
        """Test la gestion des caractères Unicode."""
        data = {
            'PN': ['RÉS001', 'CÄP002'],
            'Project': ['PRØJ_A', 'PROJ_B'],
            'Description': ['Résistance 10KΩ', 'Condensateur µF']
        }
        df = pd.DataFrame(data)
        
        cleaned_df = self.cleaner.clean_dataframe(df)
        
        # Vérifier que les caractères non-ASCII sont supprimés
        for col in ['PN', 'Project', 'Description']:
            for value in cleaned_df[col]:
                if pd.notna(value):
                    # Tous les caractères doivent être ASCII
                    self.assertTrue(all(ord(c) < 128 for c in str(value)))


if __name__ == '__main__':
    unittest.main()
