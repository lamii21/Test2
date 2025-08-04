#!/usr/bin/env python3
"""
Vérifie les statuts dans le Master BOM original
"""

import pandas as pd

def check_original_status():
    """Vérifie les statuts dans le Master BOM original."""
    
    print("🔍 VÉRIFICATION DES STATUTS ORIGINAUX")
    print("=" * 50)
    
    try:
        # Lire le Master BOM original
        df = pd.read_excel('Master_BOM_Original.xlsx')
        print(f"📊 Master BOM original: {len(df)} lignes")
        
        # Chercher les colonnes de statut
        status_columns = [col for col in df.columns if 'status' in col.lower() or 'ypn' in col.lower()]
        print(f"📋 Colonnes de statut trouvées: {status_columns}")
        
        # Vérifier YPN Status
        if 'YPN Status' in df.columns:
            print(f"\n📊 Répartition YPN Status:")
            status_counts = df['YPN Status'].value_counts(dropna=False)
            for status, count in status_counts.head(15).items():
                print(f"   • '{status}': {count} composants")
            
            # Exemples de statuts
            print(f"\n📋 Exemples de composants avec statuts:")
            sample_df = df[['Yazaki PN', 'YPN Status']].dropna().head(10)
            for _, row in sample_df.iterrows():
                print(f"   • {row['Yazaki PN']}: {row['YPN Status']}")
        
        else:
            print("❌ Colonne 'YPN Status' non trouvée")
            
        return df
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == '__main__':
    check_original_status()
