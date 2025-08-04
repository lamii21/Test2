#!/usr/bin/env python3
"""
Corrige les doublons dans le Master BOM en gardant le premier (comportement VLOOKUP)
"""

import pandas as pd

def fix_master_bom_duplicates():
    """Supprime les doublons du Master BOM."""
    
    print("🔧 CORRECTION DES DOUBLONS DANS LE MASTER BOM")
    print("=" * 50)
    
    # Lire le Master BOM
    df = pd.read_excel('Master_BOM.xlsx')
    print(f"📊 Master BOM original: {len(df)} lignes")
    
    # Identifier les doublons
    duplicates = df['PN'].duplicated()
    duplicate_count = duplicates.sum()
    print(f"🔍 Doublons détectés: {duplicate_count}")
    
    if duplicate_count > 0:
        # Afficher quelques exemples de doublons
        duplicate_pns = df[duplicates]['PN'].head(10).tolist()
        print(f"📋 Exemples de PN dupliqués: {duplicate_pns}")
        
        # Supprimer les doublons (garder le premier - comportement VLOOKUP)
        df_clean = df.drop_duplicates(subset=['PN'], keep='first')
        print(f"✅ Doublons supprimés: {len(df_clean)} lignes restantes")
        
        # Sauvegarder le Master BOM nettoyé
        df_clean.to_excel('Master_BOM.xlsx', index=False)
        print("💾 Master BOM nettoyé sauvegardé")
        
        # Statistiques
        removed = len(df) - len(df_clean)
        print(f"📊 {removed} lignes supprimées ({removed/len(df)*100:.1f}%)")
        
        # Vérifier les statuts après nettoyage
        if 'Status' in df_clean.columns:
            status_counts = df_clean['Status'].value_counts(dropna=False)
            print(f"\n📊 Répartition des statuts après nettoyage:")
            for status, count in status_counts.items():
                print(f"   • Status '{status}': {count} composants")
    
    else:
        print("✅ Aucun doublon détecté")
    
    return df_clean if duplicate_count > 0 else df

def test_cleaned_master_bom():
    """Teste le Master BOM nettoyé."""
    
    print(f"\n🧪 TEST DU MASTER BOM NETTOYÉ")
    print("=" * 50)
    
    try:
        df = pd.read_excel('Master_BOM.xlsx')
        
        # Vérifier les doublons
        duplicates = df['PN'].duplicated().sum()
        if duplicates == 0:
            print("✅ Aucun doublon détecté")
        else:
            print(f"❌ {duplicates} doublons encore présents")
            return False
        
        # Vérifier les colonnes requises
        required_columns = ['PN', 'Project', 'Status']
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            print(f"❌ Colonnes manquantes: {missing}")
            return False
        
        print("✅ Toutes les colonnes requises présentes")
        print(f"📊 {len(df)} composants uniques dans le Master BOM")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    df_clean = fix_master_bom_duplicates()
    
    if test_cleaned_master_bom():
        print(f"\n🎉 CORRECTION RÉUSSIE !")
        print(f"💡 Vous pouvez maintenant traiter vos fichiers sans erreur de doublons")
        print(f"💡 Le système utilisera le premier PN trouvé (comportement VLOOKUP)")
    else:
        print(f"\n❌ CORRECTION ÉCHOUÉE")
        print(f"💡 Vérifiez les erreurs ci-dessus")
