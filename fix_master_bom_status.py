#!/usr/bin/env python3
"""
Corrige les statuts dans le Master BOM en mappant correctement YPN Status
"""

import pandas as pd
from datetime import datetime

def fix_master_bom_status():
    """Corrige les statuts du Master BOM."""
    
    print("🔧 CORRECTION DES STATUTS MASTER BOM")
    print("=" * 50)
    
    # Lire le Master BOM original
    original_df = pd.read_excel('Master_BOM_Original.xlsx')
    print(f"📊 Master BOM original: {len(original_df)} lignes")
    
    # Mapping des statuts YPN vers nos 4 statuts
    status_mapping = {
        'Common': 'X',      # Composants communs → Actif
        'Added': '0',       # Composants ajoutés → Doublon
        'Deleted': 'D',     # Composants supprimés → Ancien
        # Vous pouvez ajuster ce mapping selon vos besoins
    }
    
    print("🎯 Mapping des statuts:")
    for original, mapped in status_mapping.items():
        count = (original_df['YPN Status'] == original).sum()
        print(f"   • '{original}' → '{mapped}': {count} composants")
    
    # Créer le DataFrame adapté avec les bons statuts
    adapted_data = {
        'PN': original_df['Yazaki PN'],
        'Project': 'FORD_J74_V710_B2_PP_YOTK_00000',  # Projet fixe
        'Description': original_df.get('Item Description', ''),
        'Supplier': original_df.get('Supplier Name', ''),
        'Status': original_df['YPN Status'].map(status_mapping).fillna('0'),  # Non mappé → Doublon
        'Last_Updated': datetime.now().strftime('%Y-%m-%d'),
        'Category': 'Component',
        'Price': 0.0,
        'Lead_Time_Days': 14,
        'Min_Order_Qty': 1
    }
    
    # Créer le DataFrame adapté
    adapted_df = pd.DataFrame(adapted_data)
    
    # Supprimer les lignes avec PN vide
    adapted_df = adapted_df.dropna(subset=['PN'])
    adapted_df = adapted_df[adapted_df['PN'] != '']
    
    print(f"📊 Master BOM adapté: {len(adapted_df)} lignes")
    
    # Statistiques des statuts finaux
    status_counts = adapted_df['Status'].value_counts(dropna=False)
    print(f"\n📈 Répartition des statuts finaux:")
    for status, count in status_counts.items():
        status_name = {
            'X': 'Actif (Common)',
            'D': 'Ancien (Deleted)',
            '0': 'Doublon (Added)',
            'NaN': 'Non mappé'
        }.get(str(status), f'Inconnu ({status})')
        print(f"   • Status '{status}' ({status_name}): {count} composants")
    
    # Sauvegarder le Master BOM corrigé
    adapted_df.to_excel('Master_BOM.xlsx', index=False)
    print("✅ Master BOM corrigé sauvegardé: Master_BOM.xlsx")
    
    return adapted_df

def test_corrected_master_bom():
    """Teste le Master BOM corrigé."""
    
    print(f"\n🧪 TEST DU MASTER BOM CORRIGÉ")
    print("=" * 50)
    
    try:
        df = pd.read_excel('Master_BOM.xlsx')
        
        # Vérifier les statuts
        status_counts = df['Status'].value_counts(dropna=False)
        print("✅ Statuts dans le Master BOM corrigé:")
        for status, count in status_counts.items():
            print(f"   • Status '{status}': {count} composants")
        
        # Vérifier qu'on a bien nos 4 statuts
        expected_statuses = {'X', 'D', '0'}
        found_statuses = set(status_counts.index)
        
        if expected_statuses.issubset(found_statuses):
            print("✅ Tous les statuts attendus sont présents")
        else:
            missing = expected_statuses - found_statuses
            print(f"⚠️ Statuts manquants: {missing}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    adapted_df = fix_master_bom_status()
    
    if test_corrected_master_bom():
        print(f"\n🎉 CORRECTION RÉUSSIE !")
        print(f"💡 Vous pouvez maintenant traiter vos fichiers avec les 4 statuts:")
        print(f"   • Status 'A': Composants actifs (Common)")
        print(f"   • Status 'D': Composants dépréciés (Added)")
        print(f"   • Status 'X': Composants anciens (Deleted)")
        print(f"   • Status '0': Doublons (à vérifier)")
        print(f"\n🚀 Testez avec: python runner.py process votre_fichier.xlsx")
    else:
        print(f"\n❌ CORRECTION ÉCHOUÉE")
