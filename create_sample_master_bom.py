#!/usr/bin/env python3
"""
Crée un Master BOM d'exemple pour tester le système
"""

import pandas as pd
from datetime import datetime

def create_sample_master_bom():
    """Crée un Master BOM d'exemple avec des données de test."""
    
    print("🔧 Création du Master BOM d'exemple...")
    
    # Données d'exemple pour le Master BOM
    sample_data = {
        'PN': [
            'YZK-001-001',
            'YZK-001-002', 
            'YZK-001-003',
            'YZK-001-004',
            'YZK-001-005',
            'YZK-002-001',
            'YZK-002-002',
            'YZK-002-003',
            'YZK-003-001',
            'YZK-003-002'
        ],
        'Project': [
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YMOK_00000',
            'FORD_J74_V710_B2_PP_YMOK_00000',
            'FORD_J74_V710_B2_PP_YMOK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000',
            'FORD_J74_V710_B2_PP_YOTK_00000'
        ],
        'Description': [
            'LT Single Wire HFSK3M Component 1',
            'LT Single Wire HFSK3M Component 2',
            'LT Single Wire HFSK3M Component 3',
            'LT Single Wire HFSK3M Component 4',
            'LT Single Wire HFSK3M Component 5',
            'LT Single Wire HFSK3M Component 6',
            'LT Single Wire HFSK3M Component 7',
            'LT Single Wire HFSK3M Component 8',
            'LT Single Wire HFSK3M Component 9',
            'LT Single Wire HFSK3M Component 10'
        ],
        'Supplier': ['Yazaki Corporation'] * 10,
        'Price': [2.50, 3.00, 1.75, 4.25, 2.80, 3.50, 2.25, 3.75, 2.90, 3.20],
        'Status': ['X', 'D', '0', 'X', 'D', 'X', '0', 'X', 'D', 'X'],
        'Last_Updated': [datetime.now().strftime('%Y-%m-%d')] * 10,
        'Category': ['Wire/Cable'] * 10,
        'Lead_Time_Days': [14] * 10,
        'Min_Order_Qty': [1000] * 10
    }
    
    # Créer le DataFrame
    df = pd.DataFrame(sample_data)
    
    # Sauvegarder le Master BOM
    filename = 'Master_BOM.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Master BOM d'exemple créé: {filename}")
    print(f"📊 Composants: {len(df)}")
    
    # Compter les statuts
    status_counts = df['Status'].value_counts()
    print(f"\n📈 Répartition des statuts:")
    for status, count in status_counts.items():
        status_name = {
            'X': 'Actif',
            'D': 'Déprécié', 
            '0': 'Doublon'
        }.get(status, f'Inconnu ({status})')
        print(f"   • Status '{status}' ({status_name}): {count} composants")
    
    # Compter les projets
    project_counts = df['Project'].value_counts()
    print(f"\n🎯 Répartition des projets:")
    for project, count in project_counts.items():
        print(f"   • {project}: {count} composants")
    
    return filename

if __name__ == '__main__':
    create_sample_master_bom()
