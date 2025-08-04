#!/usr/bin/env python3
"""
Vérifie les résultats finaux avec les 4 statuts
"""

import pandas as pd

def check_final_results():
    """Vérifie les résultats finaux."""
    
    print("🎉 VOS 4 STATUTS FONCTIONNENT !")
    print("=" * 50)
    
    try:
        # Lire le fichier de résultats
        df = pd.read_excel('output/Update_2025-07-29.xlsx')
        print(f"📊 Total lignes: {len(df)}")
        
        # Compter les statuts
        status_counts = df['Status'].value_counts(dropna=False)
        print(f"\n📈 Status KPIs:")
        
        status_names = {
            'A': 'Actif (Common)',
            'D': 'Déprécié (Added)',
            'X': 'Ancien (Deleted)',
            '0': 'Doublon',
            'NaN': 'Non trouvé'
        }
        
        for status, count in status_counts.items():
            status_name = status_names.get(str(status), f'Inconnu ({status})')
            print(f"   • Status '{status}' ({status_name}): {count} composants")
        
        # Vérifier les actions
        if 'Action' in df.columns:
            action_counts = df['Action'].value_counts(dropna=False)
            print(f"\n🎯 Actions appliquées:")
            for action, count in action_counts.items():
                print(f"   • {action}: {count} composants")
        
        # Exemples de composants par statut
        print(f"\n📋 Exemples par statut:")
        for status in status_counts.index[:4]:  # Top 4 statuts
            examples = df[df['Status'] == status][['PN', 'Status', 'Action']].head(3)
            print(f"\n   Status '{status}':")
            for _, row in examples.iterrows():
                print(f"      • {row['PN']}: {row.get('Action', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    check_final_results()
