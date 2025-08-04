#!/usr/bin/env python3
"""
Crée un Master BOM avec plusieurs colonnes de projet pour tester la sélection dynamique
"""

import pandas as pd
from datetime import datetime

def create_multi_project_master_bom():
    """Crée un Master BOM avec plusieurs colonnes de projet."""
    
    print("🔧 CRÉATION D'UN MASTER BOM MULTI-PROJETS")
    print("=" * 50)
    
    # Lire le Master BOM actuel
    current_df = pd.read_excel('Master_BOM.xlsx')
    print(f"📊 Master BOM actuel: {len(current_df)} lignes")
    
    # Créer plusieurs colonnes de projet
    multi_project_data = current_df.copy()
    
    # Ajouter différentes colonnes de projet
    multi_project_data['Ford_Project'] = 'FORD_J74_V710_B2_PP_YOTK_00000'
    multi_project_data['Customer_Project'] = 'Ford_Customer_Project_2025'
    multi_project_data['Internal_Project'] = 'YZK_Internal_V710_B2'
    multi_project_data['Program_Code'] = 'J74_V710_B2_PP'
    
    # Modifier quelques lignes pour avoir des projets différents
    # Prendre 10% des lignes pour un autre projet
    sample_size = len(multi_project_data) // 10
    if sample_size > 0:
        multi_project_data.loc[:sample_size, 'Ford_Project'] = 'FORD_J74_V710_B2_PP_YMOK_00000'
        multi_project_data.loc[:sample_size, 'Customer_Project'] = 'Ford_Customer_Project_2024'
        multi_project_data.loc[:sample_size, 'Internal_Project'] = 'YZK_Internal_V710_B2_ALT'
        multi_project_data.loc[:sample_size, 'Program_Code'] = 'J74_V710_B2_ALT'
    
    # Sauvegarder le Master BOM multi-projets
    multi_project_data.to_excel('Master_BOM_Multi_Projects.xlsx', index=False)
    print(f"✅ Master BOM multi-projets créé: Master_BOM_Multi_Projects.xlsx")
    
    # Statistiques
    print(f"\n📊 Colonnes de projet créées:")
    project_columns = ['Project', 'Ford_Project', 'Customer_Project', 'Internal_Project', 'Program_Code']
    
    for col in project_columns:
        if col in multi_project_data.columns:
            unique_values = multi_project_data[col].nunique()
            sample_values = multi_project_data[col].unique()[:3]
            print(f"   • {col}: {unique_values} valeurs uniques")
            print(f"     Exemples: {list(sample_values)}")
    
    print(f"\n💡 UTILISATION:")
    print(f"   • Copiez Master_BOM_Multi_Projects.xlsx vers Master_BOM.xlsx")
    print(f"   • Testez avec différentes colonnes:")
    print(f"     python runner.py process fichier.xlsx --project-column \"Ford_Project\"")
    print(f"     python runner.py process fichier.xlsx --project-column \"Customer_Project\"")
    print(f"     python runner.py process fichier.xlsx --project-column \"Internal_Project\"")
    
    return multi_project_data

if __name__ == '__main__':
    create_multi_project_master_bom()
