#!/usr/bin/env python3
"""
Crée un Master BOM plus complet avec plus de composants de votre fichier
pour tester le lookup sur plus de lignes
"""

import pandas as pd
from datetime import datetime

def create_full_master_bom():
    """Crée un Master BOM avec plus de composants de votre fichier."""
    
    print("Création d'un Master BOM plus complet...")
    
    # Lire votre fichier pour récupérer plus de PN
    input_df = pd.read_excel('frontend/uploads/20250729_094812_PP_B2_GPDB_BOM.xlsx')
    
    # Prendre les 50 premiers PN de votre fichier
    sample_pns = input_df['YAZAKI PN'].head(50).tolist()
    
    # Créer des statuts variés pour ces composants
    statuses = []
    for i, pn in enumerate(sample_pns):
        if i % 4 == 0:
            statuses.append('X')  # Ancien
        elif i % 4 == 1:
            statuses.append('D')  # Déprécié
        elif i % 4 == 2:
            statuses.append('0')  # Doublon
        else:
            statuses.append('X')  # Ancien
    
    # Données du Master BOM étendu
    master_data = {
        'PN': sample_pns,
        'Project': ['FORD_J74_V710_B2_PP_YOTK_00000'] * len(sample_pns),
        'Description': [f'LT Single Wire HFSK3M Component {i+1}' for i in range(len(sample_pns))],
        'Supplier': ['Yazaki Corporation'] * len(sample_pns),
        'Price': [2.50] * len(sample_pns),
        'Status': statuses,
        'Last_Updated': [datetime.now().strftime('%Y-%m-%d')] * len(sample_pns),
        'Category': ['Wire/Cable'] * len(sample_pns),
        'Lead_Time_Days': [14] * len(sample_pns),
        'Min_Order_Qty': [1000] * len(sample_pns)
    }
    
    # Créer le DataFrame
    df = pd.DataFrame(master_data)
    
    # Sauvegarder le Master BOM
    filename = 'Master_BOM.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Master BOM étendu créé: {filename}")
    print(f"📊 Composants: {len(df)}")
    
    # Compter les statuts
    status_counts = df['Status'].value_counts()
    print(f"\n📈 Répartition des statuts:")
    for status, count in status_counts.items():
        print(f"   • Status '{status}': {count} composants")
    
    print(f"\n🔍 Correspondances attendues:")
    print(f"   • {len(sample_pns)} composants seront trouvés dans le Master BOM")
    print(f"   • {355 - len(sample_pns)} composants seront NaN (nouveaux)")
    print(f"   • Plus de variété dans les statuts X, D, 0")
    
    return filename

if __name__ == '__main__':
    create_full_master_bom()
