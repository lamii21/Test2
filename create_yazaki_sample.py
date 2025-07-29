#!/usr/bin/env python3
"""
Crée un fichier d'exemple avec les noms de colonnes Yazaki
"""

import pandas as pd
from pathlib import Path

def create_yazaki_sample():
    """Crée un fichier d'exemple avec les colonnes Yazaki."""
    
    # Données d'exemple avec vos noms de colonnes
    data = {
        'Yazaki Part Number': [
            'YZK-001-A',
            'YZK-002-B', 
            'YZK-003-C',
            'YZK-004-D',
            'YZK-005-E',
            'YZK-006-F',
            'YZK-007-G',
            'YZK-008-H',
            'YZK-009-I',
            'YZK-010-J'
        ],
        'BOM As Filter': [
            'Project_Alpha',
            'Project_Beta',
            'Project_Alpha',
            'Project_Gamma',
            'Project_Beta',
            'Project_Alpha',
            'Project_Delta',
            'Project_Beta',
            'Project_Gamma',
            'Project_Alpha'
        ],
        'Description': [
            'Connector Type A',
            'Wire Harness B',
            'Terminal C',
            'Connector Type D',
            'Wire Harness E',
            'Terminal F',
            'Connector Type G',
            'Wire Harness H',
            'Terminal I',
            'Connector Type J'
        ],
        'Price': [
            12.50,
            8.75,
            3.25,
            15.00,
            9.50,
            4.00,
            18.25,
            11.00,
            5.75,
            13.50
        ],
        'Supplier': [
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp',
            'Yazaki Corp'
        ]
    }
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    # Sauvegarder le fichier
    filename = 'Yazaki_Sample_Data.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Fichier créé: {filename}")
    print(f"📊 Lignes: {len(df)}")
    print(f"📋 Colonnes: {list(df.columns)}")
    print("\n🎯 Ce fichier utilise vos noms de colonnes:")
    print("   • 'Yazaki Part Number' → sera mappé vers 'PN'")
    print("   • 'BOM As Filter' → sera mappé vers 'Project'")
    print("\n🚀 Vous pouvez maintenant tester ce fichier dans l'interface web !")
    
    return filename

if __name__ == '__main__':
    create_yazaki_sample()
