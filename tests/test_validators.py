"""
Tests unitaires pour le module DataValidator.
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.validators import DataValidator


class TestDataValidator(unittest.TestCase):
    """Tests pour la classe DataValidator."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.validator = DataValidator()
    
    def test_validate_part_number_valid(self):
        """Test la validation de numéros de pièce valides."""
        valid_pns = ['RES001', 'CAP-002', 'IC_003', 'LED123', 'CONN-456_789']
        
        for pn in valid_pns:
            is_valid, error = self.validator.validate_part_number(pn)
            self.assertTrue(is_valid, f"PN '{pn}' devrait être valide: {error}")
            self.assertEqual(error, "")
    
    def test_validate_part_number_invalid(self):
        """Test la validation de numéros de pièce invalides."""
        invalid_cases = [
            ('', 'Numéro de pièce vide'),
            (None, 'Numéro de pièce manquant'),
            (np.nan, 'Numéro de pièce manquant'),
            ('   ', 'Numéro de pièce vide'),
            ('RES@001', 'Format de numéro de pièce invalide'),
            ('A' * 51, 'Numéro de pièce trop long')
        ]
        
        for pn, expected_error_type in invalid_cases:
            is_valid, error = self.validator.validate_part_number(pn)
            self.assertFalse(is_valid, f"PN '{pn}' devrait être invalide")
            self.assertIn(expected_error_type.split()[0].lower(), error.lower())
    
    def test_validate_project_valid(self):
        """Test la validation de noms de projet valides."""
        valid_projects = ['PROJ_A', 'PROJECT_123', 'TEST-PROJECT', 'SIMPLE']
        
        for project in valid_projects:
            is_valid, error = self.validator.validate_project(project)
            self.assertTrue(is_valid, f"Project '{project}' devrait être valide: {error}")
            self.assertEqual(error, "")
    
    def test_validate_project_invalid(self):
        """Test la validation de noms de projet invalides."""
        invalid_cases = [
            ('', 'Nom de projet vide'),
            (None, 'Nom de projet manquant'),
            (np.nan, 'Nom de projet manquant'),
            ('   ', 'Nom de projet vide'),
            ('A' * 101, 'Nom de projet trop long')
        ]
        
        for project, expected_error_type in invalid_cases:
            is_valid, error = self.validator.validate_project(project)
            self.assertFalse(is_valid, f"Project '{project}' devrait être invalide")
            self.assertIn(expected_error_type.split()[0].lower(), error.lower())
    
    def test_validate_price_valid(self):
        """Test la validation de prix valides."""
        valid_prices = [0.0, 0.05, 1.50, 100.0, 9999.99, np.nan]  # NaN est accepté (optionnel)
        
        for price in valid_prices:
            is_valid, error = self.validator.validate_price(price)
            self.assertTrue(is_valid, f"Price '{price}' devrait être valide: {error}")
    
    def test_validate_price_invalid(self):
        """Test la validation de prix invalides."""
        invalid_cases = [
            (-1.0, 'Prix trop bas'),
            (10001.0, 'Prix trop élevé'),
            ('invalid', 'Format de prix invalide'),
            ('abc', 'Format de prix invalide')
        ]
        
        for price, expected_error_type in invalid_cases:
            is_valid, error = self.validator.validate_price(price)
            self.assertFalse(is_valid, f"Price '{price}' devrait être invalide")
            self.assertIn(expected_error_type.split()[0].lower(), error.lower())
    
    def test_validate_status_valid(self):
        """Test la validation de statuts valides."""
        valid_statuses = ['A', 'D', '0', 'X', np.nan]  # NaN est accepté
        
        for status in valid_statuses:
            is_valid, error = self.validator.validate_status(status)
            self.assertTrue(is_valid, f"Status '{status}' devrait être valide: {error}")
    
    def test_validate_status_invalid(self):
        """Test la validation de statuts invalides."""
        invalid_statuses = ['B', 'Z', '1', 'INVALID', 'active']
        
        for status in invalid_statuses:
            is_valid, error = self.validator.validate_status(status)
            self.assertFalse(is_valid, f"Status '{status}' devrait être invalide")
            self.assertIn('invalide', error.lower())
    
    def test_validate_dataframe_structure_valid(self):
        """Test la validation de structure de DataFrame valide."""
        valid_data = {
            'PN': ['RES001', 'CAP002'],
            'Project': ['PROJ_A', 'PROJ_B'],
            'Description': ['Resistor', 'Capacitor']
        }
        df = pd.DataFrame(valid_data)
        
        is_valid, errors = self.validator.validate_dataframe_structure(df)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_dataframe_structure_invalid(self):
        """Test la validation de structure de DataFrame invalide."""
        # DataFrame vide
        empty_df = pd.DataFrame()
        is_valid, errors = self.validator.validate_dataframe_structure(empty_df)
        self.assertFalse(is_valid)
        self.assertIn('vide', ' '.join(errors).lower())
        
        # Colonnes manquantes
        missing_cols_data = {'Description': ['Test']}
        missing_cols_df = pd.DataFrame(missing_cols_data)
        is_valid, errors = self.validator.validate_dataframe_structure(missing_cols_df)
        self.assertFalse(is_valid)
        self.assertTrue(any('manquantes' in error.lower() for error in errors))
        
        # Valeurs manquantes dans colonnes requises
        missing_values_data = {
            'PN': ['RES001', np.nan],
            'Project': ['PROJ_A', 'PROJ_B']
        }
        missing_values_df = pd.DataFrame(missing_values_data)
        is_valid, errors = self.validator.validate_dataframe_structure(missing_values_df)
        self.assertFalse(is_valid)
        self.assertTrue(any('manquantes' in error.lower() for error in errors))
    
    def test_validate_row_valid(self):
        """Test la validation de ligne valide."""
        valid_row = pd.Series({
            'PN': 'RES001',
            'Project': 'PROJ_A',
            'Price': 0.05,
            'Status': 'A'
        })
        
        is_valid, errors = self.validator.validate_row(valid_row)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_row_invalid(self):
        """Test la validation de ligne invalide."""
        invalid_row = pd.Series({
            'PN': '',  # Invalide
            'Project': 'PROJ_A',
            'Price': -1.0,  # Invalide
            'Status': 'INVALID'  # Invalide
        })
        
        is_valid, errors = self.validator.validate_row(invalid_row)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        
        # Vérifier que les erreurs contiennent les champs attendus
        error_text = ' '.join(errors).lower()
        self.assertIn('pn', error_text)
        self.assertIn('price', error_text)
        self.assertIn('status', error_text)
    
    def test_validate_file_format(self):
        """Test la validation du format de fichier."""
        # Créer un fichier temporaire Excel
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            
            # Créer un fichier Excel simple
            df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            df.to_excel(tmp_path, index=False)
        
        try:
            # Test fichier valide
            is_valid, error = self.validator.validate_file_format(tmp_path)
            self.assertTrue(is_valid, f"Fichier Excel devrait être valide: {error}")
            
            # Test fichier inexistant
            is_valid, error = self.validator.validate_file_format('nonexistent.xlsx')
            self.assertFalse(is_valid)
            self.assertIn('inexistant', error.lower())
            
            # Test format invalide
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as txt_file:
                txt_path = txt_file.name
                txt_file.write(b'test content')
            
            try:
                is_valid, error = self.validator.validate_file_format(txt_path)
                self.assertFalse(is_valid)
                self.assertIn('supporté', error.lower())
            finally:
                os.unlink(txt_path)
                
        finally:
            os.unlink(tmp_path)
    
    def test_get_validation_summary(self):
        """Test la génération du résumé de validation."""
        data = {
            'PN': ['RES001', '', 'CAP002'],
            'Project': ['PROJ_A', 'PROJ_B', ''],
            'Price': [0.05, -1.0, 1.50],
            'Status': ['A', 'INVALID', 'D']
        }
        df = pd.DataFrame(data)
        
        summary = self.validator.get_validation_summary(df)
        
        # Vérifier que toutes les clés attendues sont présentes
        expected_keys = [
            'total_rows', 'valid_rows', 'invalid_rows',
            'missing_pn', 'missing_project', 'invalid_prices', 'invalid_statuses'
        ]
        
        for key in expected_keys:
            self.assertIn(key, summary)
            self.assertIsInstance(summary[key], int)
        
        # Vérifier les valeurs
        self.assertEqual(summary['total_rows'], 3)
        self.assertGreater(summary['invalid_rows'], 0)
        self.assertGreater(summary['missing_pn'], 0)
        self.assertGreater(summary['missing_project'], 0)


class TestDataValidatorCustomConfig(unittest.TestCase):
    """Tests pour DataValidator avec configuration personnalisée."""
    
    def test_custom_config(self):
        """Test avec une configuration personnalisée."""
        custom_config = {
            'pn_pattern': r'^TEST[0-9]+$',
            'max_pn_length': 10,
            'valid_statuses': ['ACTIVE', 'INACTIVE']
        }
        
        validator = DataValidator(custom_config)
        
        # Test avec le nouveau pattern
        is_valid, _ = validator.validate_part_number('TEST123')
        self.assertTrue(is_valid)
        
        is_valid, _ = validator.validate_part_number('RES001')
        self.assertFalse(is_valid)
        
        # Test avec les nouveaux statuts
        is_valid, _ = validator.validate_status('ACTIVE')
        self.assertTrue(is_valid)
        
        is_valid, _ = validator.validate_status('A')
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()
