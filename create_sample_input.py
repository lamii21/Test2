#!/usr/bin/env python3
"""
Crée des fichiers d'entrée d'exemple pour tester le système
"""

import pandas as pd
from datetime import datetime

def create_sample_input():
    """Crée un fichier d'entrée d'exemple."""
    
    print("📄 Création du fichier d'entrée d'exemple...")
    
    # Données d'exemple pour le fichier d'entrée
    input_data = {
        'YAZAKI PN': [
            'YZK-001-001',  # Existe dans Master BOM - Status X
            'YZK-001-002',  # Existe dans Master BOM - Status D
            'YZK-001-003',  # Existe dans Master BOM - Status 0
            'YZK-001-004',  # Existe dans Master BOM - Status X
            'YZK-999-001',  # N'existe pas dans Master BOM
            'YZK-999-002',  # N'existe pas dans Master BOM
            'YZK-001-005',  # Existe dans Master BOM - Status D
            'YZK-888-001'   # N'existe pas dans Master BOM
        ],
        'Project': [
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000'
        ],
        'Description': [
            'Test Component 1',
            'Test Component 2',
            'Test Component 3',
            'Test Component 4',
            'New Component 1',
            'New Component 2',
            'Test Component 5',
            'New Component 3'
        ],
        'Quantity': [10, 5, 8, 12, 3, 7, 15, 6],
        'Unit_Price': [2.50, 3.00, 1.75, 4.25, 0.0, 0.0, 2.80, 0.0],
        'Total_Price': [25.0, 15.0, 14.0, 51.0, 0.0, 0.0, 42.0, 0.0]
    }
    
    # Créer le DataFrame
    df = pd.DataFrame(input_data)
    
    # Sauvegarder le fichier d'entrée
    filename = 'Sample_Input_Data.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Fichier d'entrée d'exemple créé: {filename}")
    print(f"📊 Lignes: {len(df)}")
    print(f"🔍 Correspondances attendues:")
    print(f"   • 5 composants trouvés dans Master BOM")
    print(f"   • 3 composants nouveaux (NaN)")
    
    return filename

def create_additional_test_files():
    """Crée des fichiers de test supplémentaires."""
    
    print("📄 Création de fichiers de test supplémentaires...")
    
    # Fichier avec données invalides
    invalid_data = {
        'YAZAKI PN': ['', 'YZK-001-001', None, 'YZK-002-001'],
        'Project': ['', 'FORD_J74_V710_B2_PP_YOTK_00000', '', 'FORD_J74_V710_B2_PP_YOTK_00000'],
        'Description': ['Invalid 1', 'Valid Component', 'Invalid 2', 'Valid Component 2'],
        'Quantity': [0, 5, -1, 10]
    }
    
    df_invalid = pd.DataFrame(invalid_data)
    df_invalid.to_excel('Sample_Invalid_Data.xlsx', index=False)
    print("✅ Fichier de données invalides créé: Sample_Invalid_Data.xlsx")
    
    # Fichier avec nouveaux composants uniquement
    new_components_data = {
        'YAZAKI PN': [
            'YZK-NEW-001',
            'YZK-NEW-002',
            'YZK-NEW-003',
            'YZK-NEW-004'
        ],
        'Project': ['FORD_J74_V710_B2_PP_YOTK_00000'] * 4,
        'Description': [
            'New Component Type A',
            'New Component Type B',
            'New Component Type C',
            'New Component Type D'
        ],
        'Quantity': [5, 10, 3, 8],
        'Unit_Price': [0.0] * 4,
        'Total_Price': [0.0] * 4
    }
    
    df_new = pd.DataFrame(new_components_data)
    df_new.to_excel('Sample_New_Components.xlsx', index=False)
    print("✅ Fichier de nouveaux composants créé: Sample_New_Components.xlsx")
    
    return ['Sample_Invalid_Data.xlsx', 'Sample_New_Components.xlsx']

if __name__ == '__main__':
    create_sample_input()
    create_additional_test_files()
